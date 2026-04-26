# Flowchart Layout

Use `flowchart` for ordered processes and decisions.

Recommended spec:

- `nodes`: ordered from top to bottom.
- `kind`: `start`, `process`, `decision`, or `end`.
- `edges`: use `from`, `to`, and optional `label`.

Rendering behavior:

- Primary layout is top-to-bottom.
- Decisions render as diamonds.
- Start/end nodes render as rounded pills.
- Edges render with arrowheads and optional labels.
