---
name: guige-svg
description: Create polished, editable, self-contained SVG diagrams by writing SVG directly. Use for architecture diagrams, flowcharts, sequence diagrams, class or ER diagrams, org charts, mind maps, timelines, state machines, data-flow diagrams, comparison matrices, conceptual illustrations, and any request to draw or visualize structure, logic, process, or relationships. Optionally validates the SVG and exports an @2x PNG.
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge SVG Diagram

Create the final diagram by writing real SVG code directly. Do not create a JSON spec and do not invoke an automatic layout renderer. Use the bundled script only to validate the finished SVG and optionally export PNG.

## Diagram Types

| Type | Use for | Read |
|---|---|---|
| `architecture` | systems, services, topology, layered components | [architecture.md](references/architecture.md) |
| `flowchart` | workflows, decisions, lifecycle, process branches | [flowchart.md](references/flowchart.md) |
| `sequence` | actors communicating over time | [sequence.md](references/sequence.md) |
| `structural` | class, ER, component, package, or org charts | [structural.md](references/structural.md) |
| `mind-map` | central idea with hierarchical branches | [conceptual.md](references/conceptual.md#mind-map) |
| `timeline` | chronological events and periods | [timeline.md](references/timeline.md) |
| `state-machine` | states, guards, events, transitions | [conceptual.md](references/conceptual.md#state-machine) |
| `data-flow` | transformations, stores, sources, and sinks | [conceptual.md](references/conceptual.md#data-flow) |
| `illustrative` | mechanisms, comparisons, visual metaphors | [conceptual.md](references/conceptual.md#illustrative) |
| `matrix` | schedules, comparisons, grouped cards | [matrix.md](references/matrix.md) |

Always read [design-system.md](references/design-system.md), then read only the reference for the selected type. When one source needs several diagrams, choose the smallest set that gives each diagram one clear message.

## Workflow

1. Identify the reader's question and select the diagram type. For an obvious single diagram, proceed directly. Confirm once only when splitting into multiple diagrams or when the requested visual direction is materially ambiguous.
2. If the input is a file, save under `{input-file-directory}/diagram/`; otherwise use `svg/{topic-slug}/`. Save source notes only when they help preserve provenance.
3. Plan the canvas before writing: list elements, group them, choose one primary flow direction, assign approximate boxes, and reserve margins for title, legend, and annotations.
4. Write a standalone `.svg` file directly. Calculate coordinates deliberately; do not embed Mermaid, PlantUML, HTML, JavaScript, or external images.
5. Validate:

```bash
python3 {baseDir}/scripts/main.py path/to/diagram.svg --validate-only --json
```

6. Correct validation failures and inspect the rendered result for overlaps, clipped labels, crossing arrows, weak contrast, and excessive empty space.
7. Generate an @2x PNG when a raster deliverable or visual inspection is useful:

```bash
python3 {baseDir}/scripts/main.py path/to/diagram.svg --json
```

If neither `rsvg-convert` nor CairoSVG is available, keep the validated SVG and report the PNG warning. Upload only when the user asks, through the public `guige-drive-upload` CLI.

## Required SVG Contract

- Root element uses `xmlns="http://www.w3.org/2000/svg"`, a fitted `viewBox`, and no fixed root `width` or `height`.
- Include a non-empty `<title>` and `role="img"`; add `aria-labelledby` when a description is present.
- Put reusable styles, markers, gradients, filters, and patterns in `<defs>` near the top.
- Draw background and regions first, connectors next, opaque node masks and nodes after them, then labels, legend, and title.
- Embed styles and use system font fallbacks. Do not load remote fonts, stylesheets, scripts, or images.
- Keep IDs unique and every `url(#id)` or fragment reference resolvable.
- Escape `&`, `<`, and `>` in text. Never place untrusted content into markup or attributes without XML escaping.
- Prefer straight or orthogonal connectors. Route around nodes and keep labels off connector lines.
- Keep at least 30 px outer padding and enough internal spacing for CJK text.

## CLI

```text
main.py <svg-file>
  -s, --scale <0-8>     PNG scale, default 2
  -o, --output <path>   PNG output, default <svg-name>@2x.png
  --validate-only       Validate without PNG export
  --json                Print a machine-readable result
```

The validator rejects malformed XML, fixed root dimensions, missing accessibility titles, broken SVG ID references, scripts, event handlers, XML entities, `foreignObject`, and external resource loading.

## Migration from the Former Spec Renderer

The former `template`, `render --spec`, JSON schema, and fixed Python layout engine are removed. Existing JSON specs are reference material only: read their content and recreate the intended diagram as direct SVG. Do not add new callers to the retired interface.
