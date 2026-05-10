#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
BOOTSTRAPPED_ENV = "GUIGE_PICBOOK_BOOTSTRAPPED"


def _run_cli() -> None:
    sys.path.insert(0, str(SCRIPT_DIR))
    from guige_picbook.cli import app

    app()


def main() -> None:
    if os.environ.get(BOOTSTRAPPED_ENV) == "1":
        _run_cli()
        return

    sys.path.insert(0, str(SCRIPT_DIR))
    import bootstrap

    bootstrap.ensure_supported_python()

    argv = sys.argv[1:]
    command = argv[0] if argv else ""

    if command == "clean-env":
        bootstrap.clean_env()
        return

    if command == "setup":
        bootstrap.ensure_environment(with_dev="--with-dev" in argv)
        print(f"guige-picbook environment ready: {bootstrap.venv_python()}")
        return

    if command == "doctor":
        bootstrap.doctor(with_dev="--with-dev" in argv)
        return

    bootstrap.ensure_environment()
    bootstrap.exec_in_environment(argv)


if __name__ == "__main__":
    main()
