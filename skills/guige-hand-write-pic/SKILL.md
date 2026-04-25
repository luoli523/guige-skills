---
name: guige-hand-write-pic
description: Generate one-page hand-drawn educational infographics in Gui Ge's warm sketchnote style. Use when the user asks for 手绘图, 手写风图片, 手绘知识图, sketchnote, hand-drawn educational infographic, slide-summary style images, or turning content into a warm cream-paper visual summary. Creates source/analysis/structured-content/prompt files, generates the final image through the available guige image backend, and can optionally upload materials through guige-drive-upload.
version: 0.1.0
---

# Gui Ge Hand Write Pic

Generate one-page hand-drawn educational infographics with a fixed warm cream-paper sketchnote style.

This skill is for visual-first summaries. It should transform content into icons, doodles, simple diagrams, grouped cards, wavy arrows, and short labels rather than dense paragraphs.

## Defaults

| Setting | Default |
|---------|---------|
| Language | `zh` unless user content or request clearly asks otherwise |
| Working root | `hand-write-pic/{topic-slug}/` |
| Final image directory | `~/Downloads/guige-skill-imagen/` |
| Final image filename | `{topic-slug}-hand-write-pic.png` |
| Default layout | `auto` |
| Default aspect | `landscape` (`16:9`) |
| Upload behavior | Disabled by default; opt in per request or env |
| Upload backend | `guige-drive-upload` |
| Upload Drive folder | `guige-skills/guige-hand-write-pic/{topic-slug}/` |

## Style Contract

Always use the style in [prompt-template.md](references/prompt-template.md):

- warm cream paper background `#F5F0E8`
- clean sketchnote style with slight hand-drawn wobble
- no realistic elements
- high-quality slide summary feel
- pastel rounded cards: `#A8D8EA`, `#B5E5CF`, `#D5C6E0`, `#F4C7AB`
- coral red `#E8655A` for highlights, keywords, key data, and checkmarks
- black text/outlines, warm gray `#6B6B6B` annotations
- visual-first icons, doodles, simple diagrams, wavy arrows, short labels
- plenty of whitespace and one bold centered takeaway sentence in the footer

## Options

Accept CLI-style options in the user's request.

| Option | Values |
|--------|--------|
| `--layout` | `auto`, `flow`, `comparison`, `grouped-cards`, `cycle`, `timeline`, `matrix`, `pyramid` |
| `--aspect` | `landscape` (`16:9`), `portrait` (`9:16`), `square` (`1:1`), or custom ratio |
| `--lang` | Output language, e.g. `zh`, `en`, `ja`, `ko`, or another language code/name |
| `--upload` | Upload final image and materials to Google Drive after generation |
| `--no-upload` | Force local-only delivery even if `GUIGE_DRIVE_UPLOAD=1` |
| `--no-confirm` | Skip confirmation |

Parameter handling:

- Use `auto` layout unless the user explicitly asks for a structure or the content strongly implies one.
- If only some options are provided, ask only about missing choices unless `--no-confirm` or `直接生成` is present.
- If the user says `默认`, use `--layout auto --aspect landscape --lang zh`.

## Workflow

### Step 1: Setup

1. Derive a short English `topic-slug` from the topic/title.
2. Parse explicit options: `--layout`, `--aspect`, `--lang`, `--upload`, `--no-upload`, `--no-confirm`.
3. Create:
   - `hand-write-pic/{topic-slug}/`
   - `hand-write-pic/{topic-slug}/prompts/`
4. If the output directory already exists, append `-YYYYMMDD-HHMMSS`.
5. Save pasted content, URL summary, or source file content as `source-{topic-slug}.md`.

### Step 2: Analyze Content

Create `analysis.md` with:

- title
- topic
- source language and output language
- audience
- content type
- selected or recommended layout/aspect/language
- 1-3 learning objectives
- key facts, numbers, entities, and quotes to preserve exactly
- recommended visual metaphors

Strip secrets, credentials, API keys, and tokens if present.

### Step 3: Structure Content

Create `structured-content.md` with:

- title and one-line subtitle
- 3-6 visual sections
- for each section: key idea, 2-5 short labels, suggested icon/doodle/diagram
- connector labels for arrows when useful
- one bold centered takeaway sentence for the footer

Keep section labels short. Prefer 2-5 word labels. Do not overload the image with paragraphs.

### Step 4: Confirm

Confirm before generating unless the user explicitly says `--no-confirm`, `直接生成`, `不用确认`, `跳过确认`, `默认`, or equivalent.

If confirmation is needed, ask for:

- layout: default `auto`
- aspect: default `landscape`
- language: default `zh`
- upload: local only unless explicitly requested

### Step 5: Generate Prompt

Read [prompt-template.md](references/prompt-template.md), then create:

```text
prompts/hand-write-pic.md
```

Replace `<insert your content here>` with the structured content. Add the chosen layout/aspect/language near the top of the prompt.

### Step 6: Generate Image

Use the best image backend available in the current runtime:

1. Native runtime image tool, if available.
2. `guige-imagen` Python API backend, when API keys are configured or deterministic local output is required.
3. Another configured local image generation skill or script, if available.
4. If no image backend exists, stop and report the prepared prompt path.

Normalize final output by copying or moving the generated image to:

```text
~/Downloads/guige-skill-imagen/{topic-slug}-hand-write-pic.png
```

If the backend saves to a generated-images directory, copy the file to the final Downloads path and leave the original in place.

If the final Downloads file exists, append a timestamp before the extension.

### Step 7: Optional Google Drive Upload

Google Drive upload is optional and disabled by default. Use `guige-drive-upload`.

Upload only when:

- the user explicitly asks to upload
- the user passes `--upload`
- `GUIGE_DRIVE_UPLOAD=1` is set

Do not upload when the user passes `--no-upload`.

When upload is enabled, invoke:

```bash
python3 skills/guige-drive-upload/scripts/main.py \
  --skill guige-hand-write-pic \
  --task "{topic-slug}" \
  --paths \
    ~/Downloads/guige-skill-imagen/{topic-slug}-hand-write-pic.png \
    hand-write-pic/{topic-slug}/source-{topic-slug}.md \
    hand-write-pic/{topic-slug}/analysis.md \
    hand-write-pic/{topic-slug}/structured-content.md \
    hand-write-pic/{topic-slug}/prompts/hand-write-pic.md
```

The upload backend writes to:

```text
gdrive:guige-skills/guige-hand-write-pic/{topic-slug}/
```

### Step 8: Final Report

Report:

- topic
- layout, aspect, language, image backend
- local final image path
- Google Drive path, upload skipped, or upload blocker
- generated files: source, analysis, structured content, prompt

Keep the report short.
