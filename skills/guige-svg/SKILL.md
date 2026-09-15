---
name: guige-svg
description: Create polished, editable, self-contained SVG diagrams by writing SVG directly, dark-themed by default with a light theme option. Use for architecture diagrams, flowcharts, sequence diagrams, class or ER diagrams, org charts, mind maps, timelines, state machines, data-flow diagrams, comparison matrices, conceptual illustrations, and any request to draw or visualize structure, logic, process, or relationships. Trigger on "画个图", "画个架构图", "流程图", "时序图", "diagram", "draw me a ...". Validates the SVG and exports an @2x PNG for visual inspection.
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge SVG Diagram

Write the final diagram as real SVG, starting from the bundled skeleton file. Do not create a JSON spec and do not invoke an automatic layout renderer. The bundled script validates the finished SVG and exports PNG; both steps are mandatory before delivery.

## Theme

| Option | Skeleton | When |
|---|---|---|
| `dark` (default) | `assets/skeleton-dark.svg` | technical docs, blog posts, slides on dark backgrounds |
| `light` | `assets/skeleton-light.svg` | only when the user explicitly asks for 浅色 / light / 白底 |

Always use dark unless the user explicitly asks for light. Do not switch to light on your own because of the destination page. State the chosen theme in one line when presenting the result.

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

Always read [design-system.md](references/design-system.md) first, then only the reference for the selected type. When one source needs several diagrams, choose the smallest set that gives each diagram one clear message.

## Workflow

1. Identify the reader's question, select the diagram type and theme. Confirm once only when splitting into multiple diagrams or when the visual direction is materially ambiguous.
2. Choose the output path. If the input is a file, save under `{input-file-directory}/diagram/`; otherwise `svg/{topic-slug}/`.
3. Copy the skeleton to the output path:

```bash
cp {baseDir}/assets/skeleton-dark.svg path/to/diagram.svg
```

4. Plan the canvas on paper before touching the file: list every node with its class and size, assign each to a column/row on the grid from design-system.md, choose one flow direction, and write down the coordinates. Widen the viewBox if the plan does not fit in 1200 × 750.
5. Edit the skeleton: set title and desc, fill the `regions`, `connectors`, `nodes`, and `legend` groups using the primitives from design-system.md and the type reference. Keep the skeleton's `<style>` and `<defs>`.
6. Validate and export PNG in one run:

```bash
python3 {baseDir}/scripts/main.py path/to/diagram.svg --json
```

7. Open the PNG and check it against the quality gate in design-system.md. Fix and re-run until it passes. A diagram that has not been rendered and inspected is not finished.
8. Present the SVG and PNG paths and the theme used. Upload only when the user asks, through the public `guige-drive-upload` CLI.

If neither `rsvg-convert` nor CairoSVG is available, report the PNG warning and inspect the SVG by other means before delivering.

## Required SVG Contract

The skeleton already satisfies these; keep them intact while editing:

- Root uses `xmlns="http://www.w3.org/2000/svg"`, a fitted `viewBox`, `role="img"`, `aria-labelledby`, and no fixed root `width` or `height`.
- Non-empty `<title>` and `<desc>`.
- Styles, markers, and patterns live in `<style>` and `<defs>` at the top. Do not load remote fonts, stylesheets, scripts, or images; no `@import`.
- Paint order: background, title, regions, connectors, mask + node + labels, legend.
- IDs unique; every `url(#id)` resolvable.
- Escape `&`, `<`, `>` in text. XML-escape any untrusted content.
- Connectors are horizontal, vertical, or L-shaped only. Text is never rotated. Labels are never truncated.

## CLI

```text
main.py <svg-file>
  -s, --scale <0-8>     PNG scale, default 2
  -o, --output <path>   PNG output, default <svg-name>@2x.png
  --validate-only       Validate without PNG export
  --json                Print a machine-readable result
```

The validator rejects malformed XML, fixed root dimensions, missing `role="img"` or title, broken SVG ID references, scripts, event handlers, XML entities, `foreignObject`, and external resource loading. It does not check layout; that is what the PNG inspection step is for.

## Migration from the Former Spec Renderer

The former `template`, `render --spec`, JSON schema, and fixed Python layout engine are removed. Existing JSON specs are reference material only: read their content and recreate the intended diagram as direct SVG. Do not add new callers to the retired interface.
