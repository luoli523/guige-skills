# Timelines

## Choose an axis

- Horizontal for up to 8 milestones with short descriptions.
- Vertical for long descriptions, many events, or a narrow canvas.

## Horizontal layout

1. Axis line at `y=400`, from `x=80` to `x=1120`, class `.conn` with `stroke-width="2"`, no arrowhead unless the timeline continues.
2. Event markers `<circle r="7">` on the axis, evenly spaced or proportional to real time (state which in the subtitle).
3. Cards alternate above (`y=260`) and below (`y=440`) the axis, 200 × 100, connected to the marker by a vertical stub.
4. Date sits nearest the marker; then title; then one or two description lines.

```svg
<!-- marker -->
<circle class="node highlight" cx="300" cy="400" r="7"/>
<line class="conn-dim" x1="300" y1="393" x2="300" y2="360"/>
<!-- card above -->
<g transform="translate(200,260)">
  <rect class="mask" width="200" height="100" rx="6"/>
  <rect class="node primary" width="200" height="100" rx="6"/>
  <text class="sub" x="100" y="20">2024-03</text>
  <text class="label" x="100" y="44">v1.0 发布</text>
  <text class="sub" x="100" y="66">首批 200 家客户接入</text>
  <text class="sub" x="100" y="82">上线 3 个核心模块</text>
</g>
```

## Vertical layout

Axis at `x=200`. Events every 110 px from `y=130`. Date to the left of the marker, right-aligned at `x=180`. Card to the right starting at `x=230`, 320 wide.

## Durations and eras

- A span uses a translucent bar on the axis: `<rect class="node infra" x="300" y="392" width="240" height="16" rx="8"/>` with its label above.
- Group many events into eras with region boundaries or shaded bands behind the axis, labeled at the top-left of each band.
- Encode categories with class plus a legend; never with color alone.

## Density

More than 8 events: widen the canvas, split into two timelines, or roll up into eras. Do not shrink type.
