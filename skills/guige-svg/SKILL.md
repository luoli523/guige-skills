---
name: guige-svg
description: Generate clean editable SVG diagrams and visual schedules from structured content. Use when the user asks for SVG output, architecture diagrams, flowcharts, timelines, matrices, comparison tables, visual schedules, or a deterministic alternative to image generation. Produces standalone .svg files and can optionally export PNG and upload through guige-drive-upload.
---

# Gui Ge SVG

Generate standalone, editable SVG diagrams from a compact JSON spec. This skill is inspired by `baoyu-diagram`, but prefers a deterministic Python renderer: the agent prepares a structured spec and the script renders, validates, and optionally exports.

## Defaults

| Setting | Default |
|---------|---------|
| Working root | `svg/{topic-slug}/` |
| Download root | `~/Downloads/guige-skill-svg/` |
| Default theme | `guige-light` |
| Default ratio | `16:9` |
| Upload behavior | Disabled unless requested |

## Supported Types

| Type | Use for |
|------|---------|
| `matrix` | schedules, comparison tables, weekly plans, grouped cards |
| `flowchart` | process steps and decisions |
| `timeline` | chronological events |
| `architecture` | systems, services, data flow, layered diagrams |

Read the matching reference only when needed:

- `references/matrix.md`
- `references/flowchart.md`
- `references/timeline.md`
- `references/architecture.md`
- `references/spec-schema.md`

## Workflow

1. Identify diagram type and derive a short English `topic-slug`.
2. Create `svg/{topic-slug}/`.
3. Save the user input as `source.md`.
4. Create `spec.json` using `references/spec-schema.md` and the type-specific reference.
5. Render:

```bash
python3 skills/guige-svg/scripts/main.py render \
  --spec svg/{topic-slug}/spec.json \
  --svg svg/{topic-slug}/output.svg \
  --theme guige-light \
  --download \
  --json
```

6. If PNG is requested, add `--png`. PNG export is best-effort and depends on `rsvg-convert`, `cairosvg`, or another configured converter.
7. If upload is requested, call `guige-drive-upload` with the SVG, PNG if created, source, and spec.

## Spec Rules

- Keep labels short; use 2-6 words for node titles and row labels.
- Use `sections` for `matrix`, `nodes`/`edges` for `flowchart` and `architecture`, and `events` for `timeline`.
- Chinese text is supported. Keep CJK labels concise to avoid overflow.
- Use icons as semantic hints only. The renderer maps common icon names to small inline symbols.
- Prefer `guige-light` for educational or family planning visuals; use `dark-tech` for technical architecture.

## Output Rules

- Output a self-contained `.svg` with `viewBox` and no fixed `width`/`height`.
- Save local working files under `svg/{topic-slug}/`.
- Copy final deliverables to `~/Downloads/guige-skill-svg/` when `--download` is used.
- Do not depend on external images.

## CLI

```bash
# Create a starter spec
python3 skills/guige-svg/scripts/main.py template --type matrix --output svg/example/spec.json

# Render SVG
python3 skills/guige-svg/scripts/main.py render --spec svg/example/spec.json --json

# Validate spec
python3 skills/guige-svg/scripts/main.py validate --spec svg/example/spec.json
```
