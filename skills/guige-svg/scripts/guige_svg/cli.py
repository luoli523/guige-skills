from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from .export import export_png
from .renderer import render_svg, write_svg
from .themes import get_theme
from .validate import load_spec, validate_spec


DEFAULT_WORK_ROOT = Path("svg")
DEFAULT_DOWNLOAD_ROOT = Path.home() / "Downloads" / "guige-skill-svg"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-svg",
        description="Render editable SVG diagrams from JSON specs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render SVG from a JSON spec")
    render.add_argument("--spec", required=True, help="Input spec.json path")
    render.add_argument("--svg", help="Output SVG path. Default: svg/<slug>/output.svg")
    render.add_argument("--theme", choices=["guige-light", "dark-tech"], help="Theme override")
    render.add_argument("--png", action="store_true", help="Export PNG if a converter is available")
    render.add_argument("--scale", type=int, default=2, help="PNG scale factor, default: 2")
    render.add_argument("--download", action="store_true", help="Copy final files to ~/Downloads/guige-skill-svg")
    render.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")

    validate = subparsers.add_parser("validate", help="Validate a JSON spec")
    validate.add_argument("--spec", required=True, help="Input spec.json path")
    validate.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")

    template = subparsers.add_parser("template", help="Write a starter spec")
    template.add_argument("--type", required=True, choices=["matrix", "flowchart", "timeline", "architecture"])
    template.add_argument("--output", required=True, help="Output spec path")
    template.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")

    return parser


def render_command(args: argparse.Namespace) -> dict[str, Any]:
    spec_path = Path(args.spec).expanduser().resolve()
    spec = load_spec(spec_path)
    theme_name = args.theme or spec.get("theme") or "guige-light"
    get_theme(theme_name)

    svg_text = render_svg(spec, theme_name)
    svg_path = Path(args.svg).expanduser().resolve() if args.svg else default_svg_path(spec)
    write_svg(svg_path, svg_text)

    png_path: Path | None = None
    png_exported = False
    if args.png:
        png_path = export_png(svg_path, svg_path.with_suffix(".png"), args.scale)
        png_exported = png_path is not None

    download_svg: Path | None = None
    download_png: Path | None = None
    if args.download:
        DEFAULT_DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        slug = slugify(str(spec.get("title") or svg_path.stem))
        download_svg = dedupe_path(DEFAULT_DOWNLOAD_ROOT / f"{slug}.svg")
        shutil.copy2(svg_path, download_svg)
        if png_path and png_path.exists():
            download_png = dedupe_path(DEFAULT_DOWNLOAD_ROOT / f"{slug}.png")
            shutil.copy2(png_path, download_png)

    return {
        "success": True,
        "type": spec["type"],
        "theme": theme_name,
        "svg_path": str(svg_path),
        "png_path": str(png_path) if png_path else None,
        "png_exported": png_exported,
        "download_svg_path": str(download_svg) if download_svg else None,
        "download_png_path": str(download_png) if download_png else None,
    }


def validate_command(args: argparse.Namespace) -> dict[str, Any]:
    spec = load_spec(args.spec)
    validate_spec(spec)
    return {"success": True, "type": spec["type"], "title": spec["title"]}


def template_command(args: argparse.Namespace) -> dict[str, Any]:
    spec = template_spec(args.type)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"success": True, "spec_path": str(output), "type": args.type}


def default_svg_path(spec: dict[str, Any]) -> Path:
    slug = slugify(str(spec.get("title") or "diagram"))
    return (DEFAULT_WORK_ROOT / slug / "output.svg").resolve()


def dedupe_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def slugify(value: str, fallback: str = "diagram", max_length: int = 80) -> str:
    value = value.strip().casefold()
    words = re.findall(r"[a-z0-9]+", value)
    if not words:
        return fallback
    slug = "-".join(words)
    return slug[:max_length].strip("-") or fallback


def template_spec(diagram_type: str) -> dict[str, Any]:
    if diagram_type == "matrix":
        return {
            "title": "Weekly Plan",
            "subtitle": "Courses and windows",
            "type": "matrix",
            "theme": "guige-light",
            "canvas": {"ratio": "16:9"},
            "sections": [
                {
                    "title": "Mon",
                    "items": [
                        {"label": "Child A", "text": "Sports class", "icon": "school"},
                        {"label": "Child B", "text": "5:45-6:30 Swim", "icon": "swim"},
                    ],
                }
            ],
            "highlights": [{"label": "Best", "text": "Wed 5:40-7:10", "icon": "clock"}],
            "footer": "Lock the important windows first.",
        }
    if diagram_type == "flowchart":
        return {
            "title": "Decision Flow",
            "type": "flowchart",
            "theme": "guige-light",
            "nodes": [
                {"id": "start", "label": "Start", "kind": "start"},
                {"id": "check", "label": "Ready?", "kind": "decision"},
                {"id": "done", "label": "Done", "kind": "end"},
            ],
            "edges": [
                {"from": "start", "to": "check"},
                {"from": "check", "to": "done", "label": "yes"},
            ],
        }
    if diagram_type == "timeline":
        return {
            "title": "Project Timeline",
            "type": "timeline",
            "theme": "guige-light",
            "events": [
                {"date": "Week 1", "title": "Plan", "text": "Define goals"},
                {"date": "Week 2", "title": "Build", "text": "Create MVP"},
                {"date": "Week 3", "title": "Ship", "text": "Publish"},
            ],
        }
    return {
        "title": "System Architecture",
        "type": "architecture",
        "theme": "dark-tech",
        "nodes": [
            {"id": "web", "label": "Web App", "text": "UI", "group": "Client"},
            {"id": "api", "label": "API", "text": "Service", "group": "Backend"},
        ],
        "edges": [{"from": "web", "to": "api", "label": "HTTPS"}],
    }


def main(argv: list[str] | None = None) -> int:
    resolved_argv = sys.argv[1:] if argv is None else argv
    json_requested = "--json" in resolved_argv
    args = build_parser().parse_args(resolved_argv)
    try:
        if args.command == "render":
            result = render_command(args)
        elif args.command == "validate":
            result = validate_command(args)
        elif args.command == "template":
            result = template_command(args)
        else:
            raise ValueError(f"Unknown command: {args.command}")

        if json_requested:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "render":
            print(result["svg_path"])
        elif args.command == "template":
            print(result["spec_path"])
        else:
            print("Spec is valid")
        return 0
    except Exception as error:
        if json_requested:
            print(json.dumps({"success": False, "error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {error}", file=sys.stderr)
        return 1
