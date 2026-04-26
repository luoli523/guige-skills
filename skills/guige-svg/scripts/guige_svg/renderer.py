from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any

from .themes import Theme, get_theme
from .validate import validate_svg_text


def render_svg(spec: dict[str, Any], theme_name: str | None = None) -> str:
    theme = get_theme(theme_name or spec.get("theme"))
    diagram_type = spec["type"]
    if diagram_type == "matrix":
        svg = render_matrix(spec, theme)
    elif diagram_type == "flowchart":
        svg = render_flowchart(spec, theme)
    elif diagram_type == "timeline":
        svg = render_timeline(spec, theme)
    elif diagram_type == "architecture":
        svg = render_architecture(spec, theme)
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")
    validate_svg_text(svg)
    return svg


def write_svg(path: str | Path, svg: str) -> Path:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8")
    return target


def render_matrix(spec: dict[str, Any], theme: Theme) -> str:
    width, height = canvas_size(spec)
    sections = spec.get("sections", [])
    n = max(1, len(sections))
    margin = 48
    gap = 18
    title_y = 48
    subtitle_y = 82
    card_y = 128
    card_h = 430 if spec.get("highlights") else 560
    card_w = (width - margin * 2 - gap * (n - 1)) / n
    highlight_y = card_y + card_h + 34

    body: list[str] = [defs(theme), background(width, height, theme)]
    body.append(text(width / 2, title_y, spec["title"], 34, 800, theme.text, "middle"))
    if spec.get("subtitle"):
        body.append(text(width / 2, subtitle_y, spec["subtitle"], 17, 500, theme.muted, "middle"))

    for index, section in enumerate(sections):
        x = margin + index * (card_w + gap)
        fill = theme.card_fills[index % len(theme.card_fills)]
        body.append(card(x, card_y, card_w, card_h, fill, theme))
        body.append(number_badge(x + 28, card_y + 30, index + 1, theme))
        body.append(text(x + card_w / 2, card_y + 38, str(section.get("title", "")), 19, 800, theme.text, "middle"))
        items = section.get("items", [])
        row_h = max(70, (card_h - 88) / max(1, len(items)))
        y = card_y + 76
        for item in items:
            body.append(icon(item.get("icon", ""), x + 24, y + 6, 28, theme))
            body.append(text(x + 62, y + 22, str(item.get("label", "")), 13, 800, theme.text, "start"))
            lines = wrap_text(str(item.get("text", "")), max(8, int(card_w / 18)))
            for line_index, line in enumerate(lines[:3]):
                body.append(text(x + 62, y + 42 + line_index * 16, line, 12, 500, theme.text, "start"))
            y += row_h

    highlights = spec.get("highlights", [])
    if highlights:
        body.append(text(margin, highlight_y + 24, "重点", 18, 800, theme.text, "start"))
        h_gap = 16
        h_x = margin + 78
        h_w = (width - h_x - margin - h_gap * (len(highlights) - 1)) / max(1, len(highlights))
        for index, item in enumerate(highlights):
            x = h_x + index * (h_w + h_gap)
            body.append(dashed_box(x, highlight_y, h_w, 76, theme))
            body.append(icon(item.get("icon", ""), x + 18, highlight_y + 24, 24, theme))
            body.append(text(x + 50, highlight_y + 28, str(item.get("label", "")), 14, 800, theme.text, "start"))
            body.append(text(x + 50, highlight_y + 52, str(item.get("text", "")), 12, 500, theme.text, "start"))

    if spec.get("footer"):
        body.append(text(width / 2, height - 34, spec["footer"], 20, 800, theme.text, "middle"))

    return svg_root(width, height, body, theme)


def render_flowchart(spec: dict[str, Any], theme: Theme) -> str:
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    width = 1000
    height = max(620, 190 + len(nodes) * 125)
    cx = width / 2
    start_y = 130
    step_y = 120
    positions: dict[str, tuple[float, float]] = {}
    body: list[str] = [defs(theme), background(width, height, theme)]
    body.append(text(cx, 54, spec["title"], 28, 800, theme.text, "middle"))
    if spec.get("subtitle"):
        body.append(text(cx, 84, spec["subtitle"], 14, 500, theme.muted, "middle"))

    for index, node in enumerate(nodes):
        positions[str(node["id"])] = (cx, start_y + index * step_y)

    for edge in edges:
        start = positions.get(str(edge.get("from")))
        end = positions.get(str(edge.get("to")))
        if start and end:
            body.append(arrow(start[0], start[1] + 42, end[0], end[1] - 42, theme, edge.get("label")))

    for node in nodes:
        x, y = positions[str(node["id"])]
        body.append(flow_node(x, y, node, theme))

    if spec.get("footer"):
        body.append(text(cx, height - 35, spec["footer"], 16, 700, theme.text, "middle"))
    return svg_root(width, height, body, theme)


def render_timeline(spec: dict[str, Any], theme: Theme) -> str:
    events = spec.get("events", [])
    width = max(1000, 170 * len(events) + 160)
    height = 660
    axis_y = 330
    margin = 90
    step = (width - margin * 2) / max(1, len(events) - 1)
    body: list[str] = [defs(theme), background(width, height, theme)]
    body.append(text(width / 2, 54, spec["title"], 28, 800, theme.text, "middle"))
    if spec.get("subtitle"):
        body.append(text(width / 2, 84, spec["subtitle"], 14, 500, theme.muted, "middle"))
    body.append(line(margin, axis_y, width - margin, axis_y, theme.accent, 3))

    for index, event in enumerate(events):
        x = margin + index * step
        card_y = 145 if index % 2 == 0 else 380
        body.append(circle(x, axis_y, 8, theme.accent, theme))
        body.append(line(x, axis_y, x, card_y + (120 if index % 2 == 0 else 0), theme.stroke, 1.2, "4,4"))
        body.append(card(x - 80, card_y, 160, 120, theme.card_fills[index % len(theme.card_fills)], theme))
        body.append(text(x, card_y + 28, str(event.get("date", "")), 12, 800, theme.accent, "middle"))
        body.append(text(x, card_y + 54, str(event.get("title", "")), 14, 800, theme.text, "middle"))
        for line_index, wrapped in enumerate(wrap_text(str(event.get("text", "")), 12)[:2]):
            body.append(text(x, card_y + 78 + line_index * 16, wrapped, 11, 500, theme.muted, "middle"))

    if spec.get("footer"):
        body.append(text(width / 2, height - 34, spec["footer"], 16, 700, theme.text, "middle"))
    return svg_root(width, height, body, theme)


def render_architecture(spec: dict[str, Any], theme: Theme) -> str:
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    groups: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        groups.setdefault(str(node.get("group") or "System"), []).append(node)
    group_names = list(groups)
    width = max(1100, 260 * len(group_names) + 120)
    max_group_nodes = max((len(items) for items in groups.values()), default=1)
    height = max(680, 210 + max_group_nodes * 120)
    margin = 60
    group_gap = 34
    group_w = (width - margin * 2 - group_gap * (len(group_names) - 1)) / max(1, len(group_names))
    group_y = 125
    node_positions: dict[str, tuple[float, float]] = {}
    body: list[str] = [defs(theme), background(width, height, theme)]
    body.append(text(width / 2, 54, spec["title"], 28, 800, theme.text, "middle"))
    if spec.get("subtitle"):
        body.append(text(width / 2, 84, spec["subtitle"], 14, 500, theme.muted, "middle"))

    for group_index, group_name in enumerate(group_names):
        gx = margin + group_index * (group_w + group_gap)
        gh = height - group_y - 100
        body.append(region(gx, group_y, group_w, gh, group_name, theme))
        for node_index, node in enumerate(groups[group_name]):
            nx = gx + group_w / 2
            ny = group_y + 70 + node_index * 105
            node_positions[str(node["id"])] = (nx, ny)

    for edge in edges:
        start = node_positions.get(str(edge.get("from")))
        end = node_positions.get(str(edge.get("to")))
        if start and end:
            body.append(arrow(start[0] + 82, start[1], end[0] - 82, end[1], theme, edge.get("label")))

    for group_name in group_names:
        for node in groups[group_name]:
            x, y = node_positions[str(node["id"])]
            body.append(service_box(x - 82, y - 32, 164, 64, node, theme))

    if spec.get("footer"):
        body.append(text(width / 2, height - 34, spec["footer"], 16, 700, theme.text, "middle"))
    return svg_root(width, height, body, theme)


def canvas_size(spec: dict[str, Any]) -> tuple[int, int]:
    ratio = str(spec.get("canvas", {}).get("ratio") or "16:9")
    if ratio == "1:1":
        return 1100, 1100
    if ratio == "4:3":
        return 1200, 900
    if ratio == "9:16":
        return 900, 1600
    return 1600, 900


def svg_root(width: int, height: int, body: list[str], theme: Theme) -> str:
    content = "\n".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="diagram">\n{content}\n</svg>\n'
    )


def defs(theme: Theme) -> str:
    return f"""<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{theme.grid}" stroke-width="0.6" opacity="0.5"/>
  </pattern>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="{theme.stroke}"/>
  </marker>
  <style>
    text {{ font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; }}
  </style>
</defs>"""


def background(width: int, height: int, theme: Theme) -> str:
    return (
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{theme.background}"/>'
        f'\n<rect x="0" y="0" width="{width}" height="{height}" fill="url(#grid)" opacity="0.35"/>'
    )


def card(x: float, y: float, w: float, h: float, fill: str, theme: Theme) -> str:
    return (
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="18" '
        f'fill="{fill}" opacity="0.38" stroke="{theme.stroke}" stroke-width="1.8"/>'
    )


def dashed_box(x: float, y: float, w: float, h: float, theme: Theme) -> str:
    return (
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="14" '
        f'fill="none" stroke="{theme.stroke}" stroke-width="1.5" stroke-dasharray="7,5"/>'
    )


def region(x: float, y: float, w: float, h: float, label: str, theme: Theme) -> str:
    return (
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="18" '
        f'fill="none" stroke="{theme.accent}" stroke-width="1.4" stroke-dasharray="9,5"/>'
        f'\n{text(x + 16, y + 26, label, 13, 800, theme.accent, "start")}'
    )


def service_box(x: float, y: float, w: float, h: float, node: dict[str, Any], theme: Theme) -> str:
    lines = [card(x, y, w, h, theme.card_fills[0], theme)]
    lines.append(text(x + w / 2, y + 26, str(node.get("label", "")), 13, 800, theme.text, "middle"))
    if node.get("text"):
        lines.append(text(x + w / 2, y + 46, str(node.get("text", "")), 10, 500, theme.muted, "middle"))
    return "\n".join(lines)


def flow_node(cx: float, cy: float, node: dict[str, Any], theme: Theme) -> str:
    kind = node.get("kind", "process")
    label = str(node.get("label", ""))
    if kind == "decision":
        return (
            f'<polygon points="{fmt(cx)},{fmt(cy - 45)} {fmt(cx + 70)},{fmt(cy)} '
            f'{fmt(cx)},{fmt(cy + 45)} {fmt(cx - 70)},{fmt(cy)}" '
            f'fill="{theme.card_fills[3]}" opacity="0.36" stroke="{theme.accent}" stroke-width="1.8"/>'
            f'\n{text(cx, cy + 4, label, 12, 800, theme.text, "middle")}'
        )
    rx = 18 if kind in {"start", "end"} else 12
    fill = theme.card_fills[1] if kind in {"start", "end"} else theme.card_fills[0]
    return (
        f'<rect x="{fmt(cx - 105)}" y="{fmt(cy - 34)}" width="210" height="68" rx="{rx}" '
        f'fill="{fill}" opacity="0.38" stroke="{theme.stroke}" stroke-width="1.8"/>'
        f'\n{text(cx, cy + 5, label, 13, 800, theme.text, "middle")}'
    )


def arrow(x1: float, y1: float, x2: float, y2: float, theme: Theme, label: Any = None) -> str:
    path = (
        f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
        f'stroke="{theme.stroke}" stroke-width="1.6" marker-end="url(#arrow)"/>'
    )
    if label:
        path += "\n" + text((x1 + x2) / 2, (y1 + y2) / 2 - 8, str(label), 10, 600, theme.muted, "middle")
    return path


def line(x1: float, y1: float, x2: float, y2: float, color: str, width: float, dash: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
        f'stroke="{color}" stroke-width="{fmt(width)}"{dash_attr}/>'
    )


def circle(cx: float, cy: float, radius: float, fill: str, theme: Theme) -> str:
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(radius)}" fill="{fill}" stroke="{theme.stroke}" stroke-width="1.2"/>'


def number_badge(cx: float, cy: float, value: int, theme: Theme) -> str:
    return (
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="18" fill="{theme.accent}" opacity="0.95"/>'
        f'\n{text(cx, cy + 5, str(value), 16, 800, "#FFFFFF", "middle")}'
    )


def icon(kind: str, x: float, y: float, size: float, theme: Theme) -> str:
    key = (kind or "note").lower()
    s = size
    stroke = theme.stroke
    accent = theme.accent
    if key in {"swim", "pool", "goggles"}:
        return (
            f'<path d="M {fmt(x)} {fmt(y+s*0.65)} q {fmt(s*0.2)} -8 {fmt(s*0.4)} 0 t {fmt(s*0.4)} 0" '
            f'fill="none" stroke="{accent}" stroke-width="2"/>'
            f'\n<circle cx="{fmt(x+s*0.35)}" cy="{fmt(y+s*0.3)}" r="{fmt(s*0.16)}" fill="none" stroke="{stroke}" stroke-width="1.5"/>'
            f'\n<circle cx="{fmt(x+s*0.65)}" cy="{fmt(y+s*0.3)}" r="{fmt(s*0.16)}" fill="none" stroke="{stroke}" stroke-width="1.5"/>'
        )
    if key in {"run", "shoe", "running"}:
        return (
            f'<path d="M {fmt(x+s*0.1)} {fmt(y+s*0.58)} h {fmt(s*0.48)} q {fmt(s*0.24)} 0 {fmt(s*0.3)} {fmt(s*0.16)} '
            f'h {fmt(-s*0.82)} q {fmt(s*0.06)} {fmt(-s*0.24)} {fmt(s*0.04)} {fmt(-s*0.32)}" '
            f'fill="none" stroke="{accent}" stroke-width="2" stroke-linejoin="round"/>'
        )
    if key in {"school", "building"}:
        return (
            f'<path d="M {fmt(x+s*0.15)} {fmt(y+s*0.48)} l {fmt(s*0.35)} {fmt(-s*0.25)} l {fmt(s*0.35)} {fmt(s*0.25)}" '
            f'fill="none" stroke="{stroke}" stroke-width="1.5"/>'
            f'\n<rect x="{fmt(x+s*0.22)}" y="{fmt(y+s*0.48)}" width="{fmt(s*0.56)}" height="{fmt(s*0.34)}" fill="none" stroke="{stroke}" stroke-width="1.5"/>'
        )
    if key in {"piano", "music"}:
        return (
            f'<rect x="{fmt(x+s*0.08)}" y="{fmt(y+s*0.28)}" width="{fmt(s*0.84)}" height="{fmt(s*0.42)}" fill="none" stroke="{stroke}" stroke-width="1.5"/>'
            f'\n<path d="M {fmt(x+s*0.15)} {fmt(y+s*0.5)} h {fmt(s*0.7)}" stroke="{stroke}" stroke-width="1"/>'
        )
    if key in {"brush", "paint"}:
        return f'<path d="M {fmt(x+s*0.2)} {fmt(y+s*0.8)} L {fmt(x+s*0.78)} {fmt(y+s*0.2)}" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>'
    if key in {"football", "ball"}:
        return f'<circle cx="{fmt(x+s*0.5)}" cy="{fmt(y+s*0.5)}" r="{fmt(s*0.32)}" fill="none" stroke="{stroke}" stroke-width="1.8"/>'
    if key in {"book", "read"}:
        return (
            f'<path d="M {fmt(x+s*0.1)} {fmt(y+s*0.25)} q {fmt(s*0.2)} -8 {fmt(s*0.4)} 0 v {fmt(s*0.5)} q {fmt(-s*0.2)} -8 {fmt(-s*0.4)} 0 z" '
            f'fill="none" stroke="{stroke}" stroke-width="1.3"/>'
            f'\n<path d="M {fmt(x+s*0.5)} {fmt(y+s*0.25)} q {fmt(s*0.2)} -8 {fmt(s*0.4)} 0 v {fmt(s*0.5)} q {fmt(-s*0.2)} -8 {fmt(-s*0.4)} 0 z" fill="none" stroke="{stroke}" stroke-width="1.3"/>'
        )
    if key in {"moon", "night"}:
        return f'<circle cx="{fmt(x+s*0.48)}" cy="{fmt(y+s*0.44)}" r="{fmt(s*0.32)}" fill="{accent}" opacity="0.25"/><circle cx="{fmt(x+s*0.6)}" cy="{fmt(y+s*0.35)}" r="{fmt(s*0.32)}" fill="{theme.background}"/>'
    if key in {"dumbbell", "fitness"}:
        return f'<path d="M {fmt(x+s*0.2)} {fmt(y+s*0.5)} h {fmt(s*0.6)}" stroke="{accent}" stroke-width="3"/><rect x="{fmt(x+s*0.08)}" y="{fmt(y+s*0.35)}" width="{fmt(s*0.12)}" height="{fmt(s*0.3)}" fill="none" stroke="{stroke}"/><rect x="{fmt(x+s*0.8)}" y="{fmt(y+s*0.35)}" width="{fmt(s*0.12)}" height="{fmt(s*0.3)}" fill="none" stroke="{stroke}"/>'
    if key in {"clock", "stopwatch", "time"}:
        return f'<circle cx="{fmt(x+s*0.5)}" cy="{fmt(y+s*0.5)}" r="{fmt(s*0.32)}" fill="none" stroke="{stroke}" stroke-width="1.6"/><path d="M {fmt(x+s*0.5)} {fmt(y+s*0.5)} v {fmt(-s*0.18)} h {fmt(s*0.15)}" stroke="{accent}" stroke-width="1.8" fill="none"/>'
    if key in {"car"}:
        return f'<rect x="{fmt(x+s*0.15)}" y="{fmt(y+s*0.42)}" width="{fmt(s*0.7)}" height="{fmt(s*0.25)}" rx="4" fill="none" stroke="{stroke}" stroke-width="1.5"/><circle cx="{fmt(x+s*0.3)}" cy="{fmt(y+s*0.7)}" r="{fmt(s*0.08)}" fill="{stroke}"/><circle cx="{fmt(x+s*0.7)}" cy="{fmt(y+s*0.7)}" r="{fmt(s*0.08)}" fill="{stroke}"/>'
    return f'<circle cx="{fmt(x+s*0.5)}" cy="{fmt(y+s*0.5)}" r="{fmt(s*0.22)}" fill="none" stroke="{accent}" stroke-width="1.8"/>'


def text(x: float, y: float, value: Any, size: int, weight: int, fill: str, anchor: str) -> str:
    return (
        f'<text x="{fmt(x)}" y="{fmt(y)}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def wrap_text(value: str, max_units: int) -> list[str]:
    if not value:
        return []
    result: list[str] = []
    current = ""
    current_units = 0
    for char in value:
        units = 2 if ord(char) > 127 else 1
        if current and current_units + units > max_units:
            result.append(current)
            current = char
            current_units = units
        else:
            current += char
            current_units += units
    if current:
        result.append(current)
    return result


def escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def fmt(value: float) -> str:
    if math.isclose(value, round(value)):
        return str(int(round(value)))
    return f"{value:.2f}"
