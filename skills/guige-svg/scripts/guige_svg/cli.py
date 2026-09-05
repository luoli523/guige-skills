from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .export import export_png
from .validate import validate_svg_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-svg",
        description="Validate an agent-written SVG and optionally export an @2x PNG.",
    )
    parser.add_argument("svg", help="Existing standalone .svg file")
    parser.add_argument("-s", "--scale", type=float, default=2, help="PNG scale factor, default: 2")
    parser.add_argument("-o", "--output", help="PNG output path, default: <svg-name>@2x.png")
    parser.add_argument("--validate-only", action="store_true", help="Validate without exporting PNG")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def process_svg(
    svg_path: str | Path,
    output_path: str | Path | None = None,
    scale: float = 2,
    validate_only: bool = False,
) -> dict[str, Any]:
    source = Path(svg_path).expanduser().resolve()
    validation = validate_svg_file(source)
    if not isinstance(scale, (int, float)) or scale <= 0 or scale > 8:
        raise ValueError("scale must be greater than 0 and at most 8")
    if validate_only:
        return {
            "success": True,
            "svg_path": str(source),
            "png_path": None,
            "png_exported": False,
            "validation": validation,
            "warnings": [],
        }

    target = (
        Path(output_path).expanduser().resolve()
        if output_path
        else source.with_name(f"{source.stem}@2x.png")
    )
    if target == source:
        raise ValueError("PNG output path must differ from the source SVG path")
    if target.suffix.lower() != ".png":
        raise ValueError("PNG output path must use the .png extension")
    target.parent.mkdir(parents=True, exist_ok=True)
    exported = export_png(source, target, scale)
    warnings = [] if exported else [
        "PNG converter unavailable; install rsvg-convert or CairoSVG, or keep the validated SVG output."
    ]
    return {
        "success": True,
        "svg_path": str(source),
        "png_path": str(exported) if exported else None,
        "png_exported": exported is not None,
        "validation": validation,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = process_svg(args.svg, args.output, args.scale, args.validate_only)
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["png_path"] or result["svg_path"])
            for warning in result["warnings"]:
                print(f"Warning: {warning}", file=sys.stderr)
        return 0
    except Exception as error:
        if args.json_output:
            print(json.dumps({"success": False, "error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {error}", file=sys.stderr)
        return 1
