# Architecture Layout

Use `architecture` for system components, services, and data flow.

Recommended spec:

- `nodes`: include `id`, `label`, optional `text`, and optional `group`.
- `edges`: include `from`, `to`, and optional `label`.
- Use `group` to create layered regions.

Rendering behavior:

- Groups are arranged left-to-right.
- Nodes within a group stack vertically.
- Edges render behind node boxes.
- `dark-tech` is preferred for technical diagrams; `guige-light` is preferred for conceptual architecture.
