# Content-production workflows

[← Quickstart](../quickstart.md) · [Architecture](../architecture/overview.md)

This family turns a topic or source material into images, diagrams, presentations, children’s books, or blog content. Each skill’s `SKILL.md` is the invocation contract; this page explains where responsibilities meet.

## Choose the right workflow

| Need | Skill | Key output |
|---|---|---|
| Generic raster generation or edits | `guige-imagen` | `~/Downloads/guige-skill-imagen/<content-slug>.png` |
| Branded, information-dense Gui Ge visual summary | `guige-infographic` | `infographic/<slug>/` plus raster final image |
| Unbranded one-page sketchnote/knowledge card | `guige-hand-write-pic` | `hand-write-pic/<slug>/` plus raster final image |
| Exploded, cutaway, or hybrid explanatory anatomy | `guige-disassembly-diagram` | `disassembly-diagram/<slug>/` plus raster final image |
| Image-first slide deck | `guige-slides` | `slide-deck/<slug>/`, PNG slides, PPTX/PDF |
| Editable deterministic chart | `guige-svg` | `svg/<slug>/source.md`, `spec.json`, `output.svg` |
| Child-friendly researched book | `guige-picbook` | `picbook/<topic-slug>/<topic-slug>.md` and optional Slides PDF |
| Hugo blog article + illustration plan | `guige-blog-post` | External blog post directory, `image-prompts.md`, WebP assets |

## Shared image foundation

`guige-imagen` is deliberately generic; it does not apply Gui Ge character styling itself. Its implementation is under `skills/guige-imagen/scripts/`; its `SKILL.md` defines backend precedence and configuration scope.

- Provider API automation is the repeatable CLI route, with scoped OpenAI/Google configuration.
- In Codex without scoped provider keys, the skill layer prefers a built-in image tool; other interactive runtimes may use their native image tool.
- Final image names are content-derived and collision-safe. The standard destination is `~/Downloads/guige-skill-imagen/`.
- Scoped configuration precedence is CLI → `EXTEND.md` → project/user `.guige-skills/.env` → permitted environment/defaults. Ambient provider variables are ignored unless explicitly enabled. Do not weaken that isolation casually.

## Visual workflow distinctions

### Infographic, hand-write card, and disassembly diagram

These are prompt/workspace workflows layered over image generation:

- **Infographic** includes the checked-in Gui Ge character reference (`skills/guige-infographic/assets/guige.jpeg`) while keeping information hierarchy primary.
- **Hand-write picture** is intentionally unbranded. It must not inherit the character, headband, narrator, or branded reference image. Recent work added a “chubby sketch” reference/prompt option, so retain that distinction when changing templates.
- **Disassembly diagram** makes explainer visuals, not authoritative teardowns by default. Specific branded, medical, safety-critical, weapon, or otherwise high-stakes internals need user-provided or authoritative grounding; otherwise label the result schematic/explanatory.

All should preserve supplied facts/numbers, avoid secrets in prompt materials, require confirmation unless the request explicitly skips it, and retain local results when optional uploads fail. Their `source/`, `analysis/`, structured-content, and `prompts/` subdirectories make prompt provenance inspectable.

### Slides

`guige-slides` is an image-first pipeline: analyze → outline → per-slide Markdown prompts → sequential PNG generation → wrappers that merge full-slide images into PPTX/PDF. The prompts are the editable source of truth; the PPTX intentionally contains complete slide images rather than editable per-element layouts. Existing output replacements are backed up with a timestamp, and image generation should not start until prompt coverage is complete.

Relevant implementation: `skills/guige-slides/scripts/merge_to_pptx.py`, `merge_to_pdf.py`, and `test_merge.py`.

### SVG

`guige-svg` trades stylistic raster output for deterministic editable diagrams. The contract is content → JSON spec → validation/render → self-contained SVG; PNG export is optional and depends on local converters. Supported documented diagram types include matrix, flowchart, timeline, and architecture. Preserve validation: generated SVG should have a `viewBox` and no `<script>`, and it must not depend on remote images.

Relevant implementation: `skills/guige-svg/scripts/guige_svg/cli.py` and `validate.py`; tests are under `scripts/tests/test_renderer.py`.

## Research-to-publication workflows

### Picbook

`guige-picbook` builds a child-facing Markdown book from a concrete topic, optionally searches configured providers/Wikipedia, adapts content with an LLM, and can make NotebookLM Slides, Telegram delivery, or Drive uploads. Defaults currently favor English, ages 8–12, 30 pages, and 3:4 portrait. It maintains its own `skills/guige-picbook/.venv/` using `uv` when possible and otherwise `venv`/pip; update its dependencies only with its bootstrap and tests in mind.

The Markdown remains valuable even if optional remote delivery fails. The recent repository history expanded it to 30-page books with a monthly upload archive and added regression coverage—avoid treating the page count or upload structure as incidental formatting.

### Blog post

`guige-blog-post` coordinates an external Hugo repository, documented in its own contract as `luoli523.github.io`. It first reads that repository’s instructions, writes and plans illustrations, then **waits for user-generated/confirmed images** before WebP conversion, validation, commit/push, and optional WeChat draft publication. It routes visual needs to the local image/diagram/chart skills rather than assuming one fixed style. Recent history changed the image prompt/style guidance; consult `skills/guige-blog-post/references/style-guide.md` instead of reintroducing a default dark-tech look.

## Safe change checklist

- Change a prompt or visual policy in the owning skill’s `SKILL.md`/`references/`, not in `guige-imagen` unless the backend contract itself changes.
- Keep output folder naming and local-first behavior stable for downstream automation.
- For Python-backed skills, run their focused test suite (listed in [Engineering guide](../engineering.md)).
- For integration-affecting changes, verify the corresponding `--json`, `--dry-run`, or prompt-only path before using a live provider/upload.
- Preserve the documented picbook archive exception: it uses `drive:Rakuten Kobo/YYYYMM` with Drive uploader `--layout task`, rather than the generic `gdrive:guige-skills/<skill>/<task>` default. This behavior was introduced with the 30-page workflow expansion (commit `ac04224`).
