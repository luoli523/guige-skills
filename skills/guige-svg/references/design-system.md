# SVG Design System

Every diagram starts from a skeleton file, never from a blank document:

- dark (default): `assets/skeleton-dark.svg`
- light: `assets/skeleton-light.svg`

Copy the chosen skeleton to the output path, then fill the `regions`, `connectors`, `nodes`, and `legend` groups and edit the title block. Keep the `<style>` classes and `<defs>` markers; add new ones only when a diagram needs them. Everything below assumes those class names exist.

## Themes

| Role | Dark (default) | Light |
|---|---|---|
| background | `#0f172a` | `#f8fafc` |
| grid | `#1e293b` | `#e2e8f0` |
| main text | `#f8fafc` | `#0f172a` |
| muted text | `#94a3b8` | `#64748b` |
| connector | `#64748b` | `#64748b` |
| lifeline / divider | `#334155` | `#cbd5e1` |

Semantic node classes (fill alpha stays low so the grid shows through and boxes read as glass, not bricks):

| Class | Meaning | Dark stroke | Light stroke |
|---|---|---|---|
| `.primary` | client, frontend, input, actor | `#22d3ee` | `#0891b2` |
| `.secondary` | service, backend, process | `#34d399` | `#059669` |
| `.data` | database, storage, cache | `#a78bfa` | `#7c3aed` |
| `.infra` | cloud, region, decision | `#fbbf24` | `#d97706` |
| `.alert` | security, error, failure | `#fb7185` | `#e11d48` |
| `.bus` | queue, event bus, middleware | `#fb923c` | `#ea580c` |
| `.neutral` | external, generic | `#94a3b8` | `#64748b` |
| `.highlight` | start/end, active, current step | `#60a5fa` | `#2563eb` |

Do not invent new colors. Do not use color as the only carrier of meaning. In flowcharts and sequence diagrams assign classes by role, not by technology.

## Canvas and fixed dimensions

- Default `viewBox="0 0 1200 750"`. Grow the canvas to fit content; never shrink type below the sizes here.
- Outer padding 40 px. Title block at `x=40 y=44` (title) and `y=64` (subtitle). Content starts at `y=100`.
- Standard node: `160 × 60`, `rx=6`. Large node: `200 × 80` to `200 × 120`. Compact node: `120 × 44`.
- Gaps: 40 px vertical and 60 px horizontal between nodes; 20 px region padding; 20 px between the lowest content and the legend.
- Columns (left-to-right layouts): 220 px between column starts. Rows (top-to-bottom): 120 px between row starts.
- Font sizes are fixed by class: title 22, group 12, label 13, sub 10, annotation 10, edge label 10, legend 10. Use `class`, not inline `font-size`.
- CJK characters are about 1.0 × font-size wide; Latin about 0.6 ×. Budget: a 160-wide box fits 11 CJK or 20 Latin characters at 13 px. If a label does not fit, widen the box or wrap with `<tspan>`. Never truncate with an ellipsis and never indent with full-width spaces.

## Layer order

Paint back-to-front in this order and keep each layer inside its skeleton group:

1. background + grid (already in skeleton)
2. title block
3. region boundaries
4. connectors
5. mask rect + node rect + node text, per node
6. legend and caption

The mask rect is mandatory: without it, connectors show through the translucent node fill.

## Primitives

Standard node:

```svg
<g transform="translate(240,140)">
  <rect class="mask" width="160" height="60" rx="6"/>
  <rect class="node secondary" width="160" height="60" rx="6"/>
  <text class="label" x="80" y="26">Order Service</text>
  <text class="sub" x="80" y="44">Go · gRPC</text>
</g>
```

Single-line node: put the label at `y=35` and omit `.sub`.

Decision diamond (100 × 70):

```svg
<g transform="translate(600,320)">
  <polygon class="mask" points="0,-35 50,0 0,35 -50,0"/>
  <polygon class="node infra" points="0,-35 50,0 0,35 -50,0"/>
  <text class="label" y="4">库存充足?</text>
</g>
```

Database cylinder (120 × 70):

```svg
<g transform="translate(900,140)">
  <rect class="mask" y="10" width="120" height="50"/>
  <ellipse class="mask" cx="60" cy="10" rx="60" ry="10"/>
  <ellipse class="mask" cx="60" cy="60" rx="60" ry="10"/>
  <rect class="node data" y="10" width="120" height="50" stroke="none"/>
  <ellipse class="node data" cx="60" cy="60" rx="60" ry="10"/>
  <ellipse class="node data" cx="60" cy="10" rx="60" ry="10"/>
  <line class="node data" x1="0" y1="10" x2="0" y2="60"/>
  <line class="node data" x1="120" y1="10" x2="120" y2="60"/>
  <text class="label" x="60" y="42">PostgreSQL</text>
</g>
```

Region boundary with label at the inside top-left:

```svg
<rect class="region" x="200" y="100" width="520" height="300" rx="12" stroke="#fbbf24"/>
<text class="region-label" x="212" y="118" fill="#fbbf24">Kubernetes Cluster</text>
```

Security boundary: same, with `stroke="#fb7185" stroke-dasharray="4 4"`.

Bus bar (shared queue between layers):

```svg
<rect class="mask" x="200" y="330" width="600" height="14" rx="7"/>
<rect class="node bus" x="200" y="330" width="600" height="14" rx="7"/>
<text class="edge" x="500" y="324">Kafka · order-events</text>
```

Number badge (sequence steps, ordered phases):

```svg
<circle cx="380" cy="200" r="9" class="node highlight"/>
<text class="edge" x="380" y="203.5" fill="#60a5fa">3</text>
```

Legend row (bottom, outside all regions):

```svg
<g id="legend" transform="translate(40,690)">
  <rect class="node primary" width="14" height="14" rx="3"/>
  <text class="legend" x="20" y="11">Client</text>
  <rect class="node secondary" x="100" width="14" height="14" rx="3"/>
  <text class="legend" x="120" y="11">Service</text>
</g>
```

## Connector rules

- Only horizontal, vertical, or L-shaped orthogonal paths. Diagonal lines are not allowed except for mind-map curves.
- Start and end at the midpoint of a node edge, with a 4 px gap from the stroke: `M 400,170 L 460,170` for a node whose right edge is at 400.
- Many-to-one: bring the many into a shared vertical or horizontal trunk first, then a single arrow into the target. Never fan four lines into one box side.

```svg
<!-- four clients on the left join a trunk at x=300, one arrow enters the target at x=380 -->
<path class="conn" d="M 260,130 L 300,130 L 300,250 L 380,250" marker-end="url(#arrow)"/>
<path class="conn" d="M 260,210 L 300,210"/>
<path class="conn" d="M 260,290 L 300,290"/>
<path class="conn" d="M 260,370 L 300,370 L 300,250"/>
```

- Edge labels sit horizontally above a horizontal segment (`y - 6`) or to the right of a vertical segment (`x + 8`). A label needs a segment at least 16 px longer than the text; on a shorter segment, move the label beside the trunk or onto the longest segment of the path. Never rotate text. Never put a label on a diagonal.
- Use `.conn-main` with `arrow-main` for the primary path, `.conn` for ordinary links, `.conn-dim` for secondary links, `.conn-err` with `arrow-err` for failure paths. Return or async messages use `marker-end="url(#arrow-open)"` and `stroke-dasharray="6 3"`.
- Route around nodes, not through them. A loop-back goes around the outside of the column.

## Quality gate

Render the PNG and look at it before delivering. Reject the diagram and fix it if any of these are true:

- text touches or crosses a box edge, or any label is truncated;
- any diagonal connector or rotated label exists;
- more than two connectors enter the same node edge without a trunk;
- nodes of the same role differ in size or class;
- rows or columns are not on a shared grid (misaligned by more than 2 px);
- the legend or caption sits inside a region or within 20 px of the canvas edge;
- the viewBox clips any content or leaves more than 120 px of empty band on any side.
