from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def export_png(svg_path: str | Path, png_path: str | Path | None = None, scale: int = 2) -> Path | None:
    source = Path(svg_path).expanduser().resolve()
    target = Path(png_path).expanduser().resolve() if png_path else source.with_suffix(".png")

    if shutil.which("rsvg-convert"):
        subprocess.run(
            ["rsvg-convert", "-z", str(scale), "-o", str(target), str(source)],
            check=True,
        )
        return target

    try:
        import cairosvg  # type: ignore
    except Exception:
        return None

    cairosvg.svg2png(url=str(source), write_to=str(target), scale=scale)
    return target
