from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


FORBIDDEN_ELEMENTS = {"foreignobject", "script"}
REFERENCE_PATTERN = re.compile(r"url\(\s*['\"]?#([^)'\"\s]+)['\"]?\s*\)", re.IGNORECASE)
EXTERNAL_URL_PATTERN = re.compile(r"url\(\s*['\"]?(?!#)", re.IGNORECASE)


def _local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1].lower()


def validate_svg_file(path: str | Path) -> dict[str, Any]:
    svg_path = Path(path).expanduser().resolve()
    if not svg_path.is_file() or svg_path.suffix.lower() != ".svg":
        raise ValueError(f"input must be an existing .svg file: {svg_path}")
    return validate_svg_text(svg_path.read_text(encoding="utf-8"))


def validate_svg_text(svg_text: str) -> dict[str, Any]:
    upper = svg_text.upper()
    if "<!DOCTYPE" in upper or "<!ENTITY" in upper:
        raise ValueError("SVG must not contain DOCTYPE or ENTITY declarations")
    if "<?XML-STYLESHEET" in upper:
        raise ValueError("SVG must not contain an external XML stylesheet")
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as error:
        raise ValueError(f"invalid SVG XML: {error}") from error
    if _local_name(root.tag) != "svg":
        raise ValueError("document root must be an SVG element")
    if not root.tag.startswith("{http://www.w3.org/2000/svg}"):
        raise ValueError("SVG root must declare xmlns=http://www.w3.org/2000/svg")
    if root.attrib.get("role") != "img":
        raise ValueError('SVG root must include role="img"')
    if "width" in root.attrib or "height" in root.attrib:
        raise ValueError("root SVG must omit fixed width and height attributes")

    view_box_value = root.attrib.get("viewBox")
    if not view_box_value:
        raise ValueError("SVG root must include viewBox")
    try:
        view_box = [float(value) for value in re.split(r"[\s,]+", view_box_value.strip())]
    except ValueError as error:
        raise ValueError("viewBox must contain four finite numbers") from error
    if len(view_box) != 4 or not all(math.isfinite(value) for value in view_box):
        raise ValueError("viewBox must contain four finite numbers")
    if view_box[2] <= 0 or view_box[3] <= 0:
        raise ValueError("viewBox width and height must be positive")

    ids: set[str] = set()
    references: set[str] = set()
    title = ""
    element_count = 0
    for element in root.iter():
        element_count += 1
        tag = _local_name(element.tag)
        if tag in FORBIDDEN_ELEMENTS:
            raise ValueError(f"SVG must not contain {tag} elements")
        if tag == "title" and not title:
            title = "".join(element.itertext()).strip()
        element_id = element.attrib.get("id")
        if element_id:
            if element_id in ids:
                raise ValueError(f"duplicate SVG id: {element_id}")
            ids.add(element_id)
        for raw_name, value in element.attrib.items():
            name = _local_name(raw_name)
            if name.startswith("on"):
                raise ValueError(f"SVG must not contain event handler attribute: {name}")
            if name == "href" and value and not value.startswith("#"):
                raise ValueError(f"SVG must not contain external resource reference: {value}")
            if name == "href" and value.startswith("#"):
                references.add(value[1:])
            if EXTERNAL_URL_PATTERN.search(value):
                raise ValueError(f"SVG must not contain external resource URL: {value}")
            references.update(REFERENCE_PATTERN.findall(value))
        if tag == "style":
            css = "".join(element.itertext())
            if "@import" in css.lower() or EXTERNAL_URL_PATTERN.search(css):
                raise ValueError("SVG styles must not load external resources")
            references.update(REFERENCE_PATTERN.findall(css))

    missing = sorted(references - ids)
    if missing:
        raise ValueError(f"reference points to missing SVG id: {missing[0]}")
    if not title:
        raise ValueError("SVG must include a non-empty title element for accessibility")
    return {
        "title": title,
        "view_box": view_box,
        "element_count": element_count,
        "id_count": len(ids),
    }
