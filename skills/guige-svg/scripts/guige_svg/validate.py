from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_TYPES = {"matrix", "flowchart", "timeline", "architecture"}


def load_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path).expanduser().resolve()
    try:
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {spec_path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("Spec root must be a JSON object")
    validate_spec(data)
    return data


def validate_spec(spec: dict[str, Any]) -> None:
    diagram_type = spec.get("type")
    if diagram_type not in SUPPORTED_TYPES:
        choices = ", ".join(sorted(SUPPORTED_TYPES))
        raise ValueError(f"Spec type must be one of: {choices}")

    title = spec.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Spec requires a non-empty string title")

    if diagram_type == "matrix":
        _require_list(spec, "sections")
    elif diagram_type in {"flowchart", "architecture"}:
        _require_list(spec, "nodes")
    elif diagram_type == "timeline":
        _require_list(spec, "events")


def validate_svg_text(svg_text: str) -> None:
    if "<svg" not in svg_text or "</svg>" not in svg_text:
        raise ValueError("Rendered output does not look like SVG")
    if "viewBox=" not in svg_text:
        raise ValueError("SVG root must include viewBox")
    if "<script" in svg_text.lower():
        raise ValueError("SVG must not contain script tags")


def _require_list(spec: dict[str, Any], key: str) -> None:
    value = spec.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Spec requires non-empty list field: {key}")
