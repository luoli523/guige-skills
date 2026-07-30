#!/usr/bin/env python3
"""CLI entry for guige-digital-human. Stdlib only; ffmpeg/ffprobe optional."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from guige_digital_human.cli import main

if __name__ == "__main__":
    sys.exit(main())
