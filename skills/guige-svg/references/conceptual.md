# Conceptual Diagram Modes

## Mind map

1. Central node at the canvas center, 200 × 64, `.highlight`, `.title`-sized text is not used; use `.label` at 15 px via inline `font-size="15"`.
2. First-level branches radiate to fixed anchor points; with N branches use angles evenly spaced, but snap the endpoint nodes to a grid so labels stay horizontal: right side branches at `x=820`, left side at `x=180`, rows 90 px apart.
3. Each branch has one class; its children inherit that class. Children are compact nodes 120 × 36 placed 40 px further out and stacked 46 px apart.
4. Branches are the only place curves are allowed: cubic Bézier from the center edge to the child edge, `stroke-width` 2 for level one, 1.5 for level two.

```svg
<path class="conn" d="M 700,375 C 760,375 760,200 820,200" stroke="#22d3ee" stroke-width="2"/>
```

Node size and font shrink by level: 13 → 12 → 11 px. Keep every label horizontal.

## State machine

- State: standard node `rx=12`, class by lifecycle role (`.highlight` for the current state if there is one).
- Initial: `<circle r="8">` filled with the main text color. Final: bullseye, `r=10` outline plus `r=6` filled.
- Transition labels `event [guard] / action`, omitting empty parts, horizontal, beside the segment.
- Self-transition: an orthogonal loop out of the top edge and back into the right edge, label at the corner.
- Bidirectional pairs: two separate parallel paths 16 px apart, each with its own arrowhead, never a double-headed line.
- Composite state: a `.region` boundary with the substates inside and its own label at the top-left.

Arrange states left-to-right in typical lifecycle order, exceptional states below the main row.

## Data flow

| Element | Shape |
|---|---|
| external entity | standard node `.neutral`, square corners `rx=0` |
| process | circle or `rx=30` node `.secondary`, numbered when the text references numbers |
| data store | open-ended bar: two horizontal lines with the label between, `.data` stroke |
| flow | `.conn` with arrowhead, labeled with the data name, not the verb |

Sources at left or top, processes in the middle, stores and sinks at right or bottom. One arrow per data item; merge identical items into one labeled arrow.

## Illustrative

Free composition for mechanisms, comparisons, and metaphors, still on the grid:

1. Write the one-sentence claim the picture must prove. Put it in the subtitle.
2. Choose 3-7 labeled parts. Each part is a node or a simple shape built from `<rect>`, `<circle>`, `<path>` using the semantic classes.
3. Use side-by-side panels (`.region` boundaries of equal size) for before/after or A/B comparisons; align the compared parts on the same row.
4. Callouts: a `.conn-dim` leader line with a horizontal label at its end; the leader is orthogonal, never diagonal.
5. Layered explanations stack equal-height bands with a `.group` label at the left.

Decoration never competes with the explanation. No icons drawn from memory, no gradients, no drop shadows, no rotated text. A summary sentence goes in a `.caption` line 24 px above the bottom edge, inside the padding, and counts as content the viewBox must include.
