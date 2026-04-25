from __future__ import annotations

import os
from pathlib import Path

PROVIDER_ENV_KEYS = frozenset(
    {
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_BASE_URL",
        "GOOGLE_BASE_URL",
        "OPENAI_IMAGE_MODEL",
        "GOOGLE_IMAGE_MODEL",
    }
)
ALLOW_AMBIENT_PROVIDER_ENV = "GUIGE_ALLOW_AMBIENT_PROVIDER_ENV"
CONTROL_ENV_KEYS = frozenset({ALLOW_AMBIENT_PROVIDER_ENV})


def parse_env_file(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}

    values: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        values[key] = value
    return values


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def load_env_files(cwd: Path | None = None, home: Path | None = None) -> None:
    resolved_cwd = cwd or Path.cwd()
    resolved_home = home or Path.home()

    merged = parse_env_file(resolved_home / ".guige-skills" / ".env")
    merged.update(parse_env_file(resolved_cwd / ".guige-skills" / ".env"))
    allow_ambient_provider_env = _is_truthy(os.environ.get(ALLOW_AMBIENT_PROVIDER_ENV))

    if not allow_ambient_provider_env:
        for key in PROVIDER_ENV_KEYS:
            os.environ.pop(key, None)

    for key, value in merged.items():
        if key in CONTROL_ENV_KEYS:
            continue
        if key in PROVIDER_ENV_KEYS and not allow_ambient_provider_env:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)
