# SVG Design System

Use this foundation for every diagram, then adapt density and emphasis to the content.

## Canvas and hierarchy

- Default to a landscape canvas around `1200 × 750`; derive other dimensions from content rather than forcing a ratio.
- Reserve 32-48 px outer padding, 64-90 px for the title block, and 24-40 px between groups.
- Give the reader one obvious entry point and one dominant flow direction.
- Use no more than three visual hierarchy levels: title, node label, annotation.

## Default dark technical palette

| Role | Fill | Stroke/text |
|---|---|---|
| background | `#0F172A` | grid `#1E293B` |
| primary | `rgba(8,51,68,.72)` | `#22D3EE` |
| secondary | `rgba(6,78,59,.66)` | `#34D399` |
| data | `rgba(76,29,149,.65)` | `#A78BFA` |
| infrastructure | `rgba(120,53,15,.55)` | `#FBBF24` |
| alert | `rgba(136,19,55,.62)` | `#FB7185` |
| neutral | `rgba(30,41,59,.88)` | `#94A3B8` |
| main text | — | `#F8FAFC` |
| secondary text | — | `#94A3B8` |

For a light editorial diagram, use `#F8FAFC` or `#F5F0E8` as background, `#172033` as text, and retain the semantic stroke hues at accessible contrast. Do not use color as the only carrier of meaning.

When the user wants adaptive embedding, define palette values as CSS custom properties and override them inside `@media (prefers-color-scheme: light)` or `dark`. Keep the base declarations complete so PNG converters that ignore media queries still produce a deliberate default appearance.

## Typography

Use system fallbacks only:

```css
text { font-family: "SFMono-Regular", "Cascadia Code", "Noto Sans SC", "PingFang SC", monospace; }
```

- Title: 24-32 px, 700
- Group heading: 14-17 px, 600-700
- Node label: 12-15 px, 600
- Annotation and arrow label: 10-12 px, 400-500
- Estimate CJK characters as roughly twice the width of Latin characters at the same size. Wrap manually with `<tspan>`; SVG text does not wrap automatically.

## Reusable primitives

Define arrow markers in `<defs>`: solid arrow for normal flow, open arrow for async/return, empty triangle for inheritance, filled/empty diamonds for composition and aggregation. Give each ID a diagram-specific prefix if combining SVG fragments.

Place connectors behind nodes. Where a connector crosses a semi-transparent node, draw an opaque background-colored mask underneath the node before drawing its styled rectangle.

Use these minimum clearances:

- 30 px horizontal and 40 px vertical between nodes
- 16 px between a connector label and a node boundary
- 8-12 px internal node padding
- 20 px from the lowest content to a legend

## Quality gate

Before delivery, check:

- every label fits its box and no text is clipped;
- arrowheads point toward the destination and branches are unambiguous;
- connectors do not run through labels or unrelated nodes;
- the viewBox includes all content plus outer padding;
- repeated node roles use consistent geometry and colors;
- the diagram remains legible at approximately 800 px display width.
