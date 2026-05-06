---
name: guige-slides
description: Generate reading-friendly slide deck image series from content, then merge slide images into PPTX and PDF. Use when the user asks to create slides, make a presentation, generate a deck, produce PPT/PPTX/PDF slides, or turn an article/topic into shareable slide images. Uses Gui Ge conventions, guige-imagen or runtime image generation, and optional guige-drive-upload.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge Slides

Generate professional slide decks as image-first slide series, then merge the images into PPTX and PDF.

This skill is for reading and sharing: each slide should be self-explanatory, visually complete, and useful as a standalone image. It is not a traditional editable-PowerPoint layout engine; PPTX output places one full-slide image on each page.

This skill is self-contained in `guige-skills`. Do not depend on, read from, or invoke any `baoyu-*` skill, config, environment file, or script.

## Defaults

| Setting | Default |
|---------|---------|
| Language | `zh` unless source/request clearly asks otherwise |
| Working root | `slide-deck/{topic-slug}/` |
| Aspect | `landscape` / `16:9` |
| Style | `blueprint` unless content signals suggest another preset |
| Audience | `general` |
| Slide count | based on source length, usually 8-18 |
| Image backend | `guige-imagen` when keyed; otherwise Codex/runtime image tool |
| Upload | disabled unless requested or `GUIGE_DRIVE_UPLOAD=1` |

## Options

Accept CLI-style options in the user request.

| Option | Description |
|--------|-------------|
| `--style <name>` | Preset or custom style name. See [style-system.md](references/style-system.md). |
| `--audience <type>` | `beginners`, `intermediate`, `experts`, `executives`, `general` |
| `--lang <code>` | Output language, e.g. `zh`, `en`, `ja` |
| `--slides <N>` | Target slide count, recommended 5-25, max 30 |
| `--ref <files...>` | Reference images for style, palette, or subject |
| `--outline-only` | Stop after `outline.md` |
| `--prompts-only` | Stop after prompt files |
| `--images-only` | Generate images from existing prompts |
| `--regenerate <N>` | Regenerate specific slide numbers, e.g. `3` or `2,5,8` |
| `--upload` | Upload final folder through `guige-drive-upload` |
| `--no-upload` | Force local-only output |
| `--no-confirm` | Skip option confirmation |

## File Layout

```text
slide-deck/{topic-slug}/
├── source-{topic-slug}.md
├── analysis.md
├── outline.md
├── refs/
├── prompts/
│   ├── 01-slide-cover.md
│   └── NN-slide-{slug}.md
├── 01-slide-cover.png
├── NN-slide-{slug}.png
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

Backup rule: if a file about to be overwritten exists, rename it to `<name>-backup-YYYYMMDD-HHMMSS.<ext>` before writing the replacement.

## Workflow

### Step 1: Setup And Analyze

1. Derive a 2-5 word English `topic-slug`.
2. Parse explicit options.
3. Create `slide-deck/{topic-slug}/`, `prompts/`, and `refs/`.
4. Save pasted content, URL summary, or source file content to `source-{topic-slug}.md`.
5. Load Gui Ge preferences from the first matching path:
   - `.guige-skills/guige-slides/EXTEND.md`
   - `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-slides/EXTEND.md`
   - `$HOME/.guige-skills/guige-slides/EXTEND.md`
6. Analyze source language, audience, content type, key facts, slide count, and style signals. Save `analysis.md`.
7. If `slide-deck/{topic-slug}/` already exists with generated content, ask whether to backup/regenerate, reuse prompts, regenerate images, or exit unless `--no-confirm` is present.

Use [style-system.md](references/style-system.md) for style selection and slide-count heuristics.

### Step 2: Confirm Options

Confirm before generating unless the user says `--no-confirm`, `直接生成`, `不用确认`, `跳过确认`, or equivalent.

Ask for:

- style preset or custom dimensions
- audience
- slide count
- whether to review outline before prompts
- whether to review prompts before images

Use [confirmation.md](references/confirmation.md) for concise option copy.

### Step 3: Generate Outline

Create `outline.md` using [outline-template.md](references/outline-template.md). The outline must include:

- topic, style, dimensions, audience, language, slide count
- one `<STYLE_INSTRUCTIONS>...</STYLE_INSTRUCTIONS>` block
- slide-by-slide entries with filenames
- cover and back-cover slides
- one clear narrative goal per slide

Stop here if `--outline-only`.

### Step 4: Review Outline

If outline review is enabled, show a compact table:

```text
# | Filename | Title | Type | Layout
```

Then ask whether to proceed, edit `outline.md` first, or regenerate outline.

### Step 5: Generate Prompt Files

For each slide in `outline.md`:

1. Read [base-prompt.md](references/base-prompt.md).
2. Copy the full `<STYLE_INSTRUCTIONS>` block from `outline.md`.
3. Add only that slide's content.
4. Add layout guidance from [layouts.md](references/layouts.md) when a layout is named.
5. Save as `prompts/NN-slide-{slug}.md`.

Prompt file requirement: every slide's final prompt must exist before image generation. The prompts directory is the reproducibility record.

Stop here if `--prompts-only`.

### Step 6: Review Prompts

If prompt review is enabled, show the prompts index and ask whether to proceed, edit prompts first, or regenerate prompts.

### Step 7: Generate Images

Use the best image backend available:

1. `guige-imagen` Python backend when guige-scoped API keys are configured or deterministic CLI output is required.
2. In Codex without a guige-scoped key, use the built-in image generation tool.
3. Otherwise use the current runtime's native image tool if available.
4. If no backend exists, stop and report the prompt paths.

Generate sequentially. Save or copy each generated slide image into the deck directory with the exact filename from the outline, usually `NN-slide-{slug}.png`.

For reference images, copy user-supplied files to `refs/NN-ref-{slug}.{ext}` and include them in prompt frontmatter. If the backend supports references, pass them; otherwise describe style/palette traits in the prompt.

### Step 8: Merge PPTX And PDF

Run:

```bash
python3 {baseDir}/scripts/merge_to_pptx.py slide-deck/{topic-slug}
python3 {baseDir}/scripts/merge_to_pdf.py slide-deck/{topic-slug}
```

The scripts scan `NN-slide-*.png|jpg|jpeg` files, sort by number, and create `{topic-slug}.pptx` and `{topic-slug}.pdf`.

### Step 9: Optional Upload

Upload only when `--upload`, explicit user request, or `GUIGE_DRIVE_UPLOAD=1` is present, unless `--no-upload` is passed.

```bash
python3 skills/guige-drive-upload/scripts/main.py \
  --skill guige-slides \
  --task "{topic-slug}" \
  --paths slide-deck/{topic-slug} \
  --json
```

Drive target:

```text
gdrive:guige-skills/guige-slides/{topic-slug}/
```

### Step 10: Final Report

Report:

- topic
- style, audience, language, slide count
- local deck folder
- PPTX and PDF paths
- upload folder or upload skipped
- generated prompts/images count

Keep the report short.

## Editing Existing Decks

Use [modification-guide.md](references/modification-guide.md).

Rule: update the prompt file first, regenerate the corresponding image, then re-run merge scripts. Prompt files remain the source of truth.
