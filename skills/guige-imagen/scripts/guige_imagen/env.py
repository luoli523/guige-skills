from __future__ import annotations

import os
from pathlib import Path


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


def load_env_files(cwd: Path | None = None, home: Path | None = None) -> None:
    resolved_cwd = cwd or Path.cwd()
    resolved_home = home or Path.home()

    merged = parse_env_file(resolved_home / ".guige-skills" / ".env")
    merged.update(parse_env_file(resolved_cwd / ".guige-skills" / ".env"))

    for key, value in merged.items():
        os.environ.setdefault(key, value)
