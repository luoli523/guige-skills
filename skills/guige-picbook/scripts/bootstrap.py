from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


BOOTSTRAP_VERSION = 1
BOOTSTRAPPED_ENV = "GUIGE_PICBOOK_BOOTSTRAPPED"
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENV_DIR = SKILL_DIR / ".venv"
STATE_FILE = VENV_DIR / ".guige-picbook-state.json"

CORE_REQUIREMENTS = SCRIPT_DIR / "requirements.txt"
NOTEBOOKLM_REQUIREMENTS = SCRIPT_DIR / "requirements-notebooklm.txt"
DEV_REQUIREMENTS = SCRIPT_DIR / "requirements-dev.txt"

PYTHON_CANDIDATES = ("python3.12", "python3.11", "python3.10")
REQUIRED_IMPORTS = (
    "typer",
    "rich",
    "httpx",
    "pydantic",
    "pydantic_settings",
    "openai",
    "anthropic",
    "google.generativeai",
    "tenacity",
    "notebooklm",
)


class BootstrapError(RuntimeError):
    pass


def ensure_supported_python() -> None:
    if sys.version_info >= (3, 10):
        return

    for name in PYTHON_CANDIDATES:
        candidate = shutil.which(name)
        if candidate:
            os.execv(candidate, [candidate, str(SCRIPT_DIR / "main.py"), *sys.argv[1:]])

    raise BootstrapError(
        "guige-picbook requires Python 3.10+. Install Python 3.10+ or run with python3.11."
    )


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _uv_bin() -> str | None:
    return shutil.which("uv")


def _run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    try:
        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as error:
        raise BootstrapError(
            f"Command failed with exit code {error.returncode}: {' '.join(command)}"
        ) from error


def _requirements(with_dev: bool = False) -> list[Path]:
    requirements = [CORE_REQUIREMENTS, NOTEBOOKLM_REQUIREMENTS]
    if with_dev:
        requirements.append(DEV_REQUIREMENTS)
    return requirements


def _requirements_hash(with_dev: bool = False) -> str:
    digest = hashlib.sha256()
    digest.update(f"bootstrap-v{BOOTSTRAP_VERSION}\n".encode())
    for path in _requirements(with_dev):
        digest.update(str(path.name).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _read_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_state(with_dev: bool = False) -> None:
    base_hash = _requirements_hash(False)
    dev_hash = _requirements_hash(True) if with_dev else None
    STATE_FILE.write_text(
        json.dumps(
            {
                "bootstrap_version": BOOTSTRAP_VERSION,
                "requirements_hash": dev_hash or base_hash,
                "base_requirements_hash": base_hash,
                "dev_requirements_hash": dev_hash,
                "python": str(venv_python()),
                "with_notebooklm": True,
                "with_dev": with_dev,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _state_matches(with_dev: bool = False) -> bool:
    state = _read_state()
    base_hash = state.get("base_requirements_hash") or state.get("requirements_hash")
    if state.get("bootstrap_version") != BOOTSTRAP_VERSION:
        return False
    if base_hash != _requirements_hash(False):
        return False
    if state.get("with_notebooklm") is not True:
        return False
    if not with_dev:
        return True
    return state.get("with_dev") is True and state.get("dev_requirements_hash") == _requirements_hash(
        True
    )


def _create_venv() -> None:
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
    uv = _uv_bin()
    if uv:
        _run([uv, "venv", str(VENV_DIR), "--python", sys.executable])
        return

    _run([sys.executable, "-m", "venv", str(VENV_DIR)])


def _install_requirements(with_dev: bool = False) -> None:
    uv = _uv_bin()
    requirements_args: list[str] = []
    for path in _requirements(with_dev):
        requirements_args.extend(["-r", str(path)])

    if uv:
        _run([uv, "pip", "install", "--python", str(venv_python()), *requirements_args])
        return

    py = str(venv_python())
    _run([py, "-m", "pip", "install", "--upgrade", "pip"])
    _run([py, "-m", "pip", "install", *requirements_args])


def _validate_imports(with_dev: bool = False) -> None:
    imports = list(REQUIRED_IMPORTS)
    if with_dev:
        imports.extend(["pytest", "ruff"])

    code = "\n".join([f"import {name}" for name in imports])
    result = subprocess.run([str(venv_python()), "-c", code], capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise BootstrapError(f"Dependency validation failed:\n{detail}")


def ensure_environment(with_dev: bool = False) -> None:
    if not venv_python().exists():
        print(f"Creating guige-picbook environment: {VENV_DIR}")
        _create_venv()

    if not _state_matches(with_dev):
        print("Installing guige-picbook dependencies, including NotebookLM support...")
        _install_requirements(with_dev)
        _validate_imports(with_dev)
        _write_state(with_dev)
        return

    _validate_imports(with_dev)


def exec_in_environment(argv: list[str]) -> None:
    env = os.environ.copy()
    env[BOOTSTRAPPED_ENV] = "1"
    scripts_path = str(SCRIPT_DIR)
    env["PYTHONPATH"] = (
        scripts_path
        if not env.get("PYTHONPATH")
        else f"{scripts_path}{os.pathsep}{env['PYTHONPATH']}"
    )
    os.execve(str(venv_python()), [str(venv_python()), str(SCRIPT_DIR / "main.py"), *argv], env)


def clean_env() -> None:
    if not VENV_DIR.exists():
        print(f"No guige-picbook environment found: {VENV_DIR}")
        return
    shutil.rmtree(VENV_DIR)
    print(f"Removed guige-picbook environment: {VENV_DIR}")


def doctor(with_dev: bool = False) -> None:
    print("guige-picbook doctor")
    print(f"launcher python: {sys.executable}")
    print(f"launcher version: {sys.version.split()[0]}")
    print(f"uv: {_uv_bin() or 'not found'}")
    ensure_environment(with_dev)
    print(f"venv: {VENV_DIR}")
    print(f"venv python: {venv_python()}")
    print(f"requirements hash: {_requirements_hash(with_dev)}")
    print("NotebookLM dependency: ok")
    print("core dependencies: ok")
    if with_dev:
        print("dev dependencies: ok")
