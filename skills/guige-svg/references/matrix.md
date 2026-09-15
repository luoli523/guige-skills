# Matrices and Comparison Boards

Use for feature comparisons, schedules, responsibility maps, 2 × 2 quadrants, and grouped cards.

## Grid table

1. Header row height 44, body row height 40, first column 180 wide, other columns equal width filling the canvas.
2. Header cells `.neutral`; row header cells `.neutral` with `.label` left-aligned at `x+12`.
3. Body cells have no fill; draw one `.divider` line per row boundary and per column boundary.
4. Values align on one baseline per row. Use consistent symbols: `✓` (fill `#34d399`), `✗` (`#fb7185`), `–` (muted), never mixed with words like "yes".
5. Highlight the recommended column with a `.highlight` region rectangle behind it.

```svg
<g transform="translate(60,110)">
  <rect class="node neutral" width="180" height="44" rx="4"/>
  <text class="label" x="12" y="27" text-anchor="start">能力</text>
  <rect class="node neutral" x="180" width="220" height="44" rx="4"/>
  <text class="label" x="290" y="27">方案 A</text>
  <line class="divider" x1="0" y1="84" x2="1080" y2="84"/>
</g>
```

## 2 × 2 quadrant

Axes at the canvas center, `.conn` with arrowheads at both ends. Axis labels: horizontal axis label at the right end, vertical at the top, both horizontal text. Quadrant titles at each corner in `.group`. Each item is a 140 × 40 compact node placed by its coordinates. State in the subtitle which direction is better.

## Card board

3-7 groups in columns, 2-5 cards each. Group header `.group` at the column top; cards are 200 × 64 standard nodes stacked with 16 px gaps; a `.region` boundary around each column.

Beyond that density, widen the canvas or split. Never drop below 10 px text.
