# Conceptual Diagram Modes

## Mind map

Put one central concept near the canvas center. Arrange first-level branches radially with distinct semantic colors, then place children along each branch's sector. Use smooth Bézier curves and decrease node size and font size by depth. Keep branch labels horizontal where possible.

## State machine

Use rounded rectangles for states, a filled circle for the initial state, and a bullseye for the final state. Label every transition as `event [guard] / action`, omitting empty parts. Use curved paths for self-transitions and route bidirectional transitions on separate arcs. Composite states use an outer boundary with their substates inside.

## Data flow

Use distinct shapes for external entities, processes, data stores, and flows. Label connectors with the data being moved, not implementation actions. Arrange sources on the left or top, transformations centrally, and sinks/stores on the right or bottom. Number processes only when the surrounding explanation references those numbers.

## Illustrative

Use free-form composition for mechanisms, comparisons, and intuition. Start with the explanatory claim, then choose a visual metaphor and 3-7 labeled parts. Use arrows, cutaways, magnified callouts, before/after panels, or annotated layers only when they clarify causality or structure. Decorative elements must not compete with the explanation.

An illustrative diagram is still an information diagram: preserve alignment, grouping, reading order, and accessible contrast. Avoid generating a poster full of disconnected icons.
