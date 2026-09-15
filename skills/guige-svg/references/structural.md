# Structural Diagrams

Covers class, ER, component, package diagrams, and org charts.

## Class box (three compartments, 180 wide)

Height = 36 (name) + 14 × attributes + 10 + 14 × methods + 10.

```svg
<g transform="translate(100,140)">
  <rect class="mask" width="180" height="124" rx="6"/>
  <rect class="node primary" width="180" height="124" rx="6"/>
  <text class="label" x="90" y="24">Order</text>
  <line class="divider" x1="0" y1="36" x2="180" y2="36" stroke="#22d3ee" stroke-opacity="0.5"/>
  <text class="annot" x="10" y="54">- id: UUID</text>
  <text class="annot" x="10" y="68">- total: Money</text>
  <line class="divider" x1="0" y1="80" x2="180" y2="80" stroke="#22d3ee" stroke-opacity="0.5"/>
  <text class="annot" x="10" y="98">+ pay(): Receipt</text>
  <text class="annot" x="10" y="112">+ cancel(): void</text>
</g>
```

Abstract class: italic name. Interface: `<text class="sub" x="90" y="14">«interface»</text>` and name at `y=28`. Two compartments when methods are irrelevant.

## Relationships

| Relationship | Path style | Marker |
|---|---|---|
| inheritance | solid | `marker-end="url(#inherit)"` at parent |
| implementation | `stroke-dasharray="6 3"` | `inherit` at interface |
| composition | solid | `marker-start="url(#diamond-filled)"` at owner |
| aggregation | solid | `marker-start="url(#diamond-open)"` at owner |
| dependency | dashed | `arrow-open` at target |
| association | solid | `arrow-open` or none |

Lines are orthogonal. Vertical inheritance rails: children connect up to a shared horizontal bar, one vertical from the bar into the parent bottom edge.

Multiplicity labels sit 6 px from the box edge, on the side away from the line: `<text class="annot" x="286" y="176">1..*</text>`.

## ER diagram

Two compartments: entity name, then attributes. Prefix keys: `PK id`, `FK order_id`; render `PK` lines with `font-weight="600"`.

Crow's foot at the many end:

```svg
<path class="conn" d="M 620,200 L 660,200"/>
<path class="conn" d="M 645,194 L 660,200 L 645,206"/>
<line class="conn" x1="648" y1="192" x2="648" y2="208"/>  <!-- optional: "one and only one" bar at the other end -->
```

Place the most connected entity near the center; arrange others to avoid crossing lines.

## Org chart

Top-down tree. Node 160 × 60. Level pitch 120 px. Sibling pitch 200 px. Root centered at the canvas midline.

Connect through a rail: parent bottom center down 30 px to a horizontal bar spanning the children, then vertical stubs into each child top center.

```svg
<path class="conn" d="M 600,170 L 600,200 L 400,200 L 400,230" marker-end="url(#arrow)"/>
<path class="conn" d="M 600,200 L 800,200 L 800,230" marker-end="url(#arrow)"/>
```

Color by department or level, not by person. Five or more levels: switch to a left-to-right tree.

## Sizing

Count the widest level first; width = nodes × 200 + 80. Center the tree in the viewBox and grow the canvas rather than shrinking nodes.
