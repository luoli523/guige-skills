---
name: guige-infographic
description: Generate infographics in Gui Ge's personal style as a standalone skill. Supports --layout, --style, --aspect, and --lang options; always uses the bundled Gui Ge character image from assets/guige.jpeg; creates analysis/structured content/prompts independently; generates the final infographic; and can optionally upload it to Google Drive guige-images with a content-related filename. Use for 鬼哥信息图, 中文信息图, 信息图, 高密度信息大图, visual summary, or turning article/content into a Gui Ge branded infographic.
version: 0.3.2
---

# Gui Ge Infographic

Standalone workflow for infographics with the bundled Gui Ge narrator character and optional Google Drive delivery.

This skill owns its own analysis, structure, design choices, prompt generation, image generation, and upload flow.

## Defaults

| Setting | Default |
|---------|---------|
| Language | `zh` |
| Character image | `assets/guige.jpeg` |
| Output root | `infographic/{topic-slug}/` |
| Default layout | `dense-modules` |
| Default style | `guige-journal` |
| Default aspect | `landscape` (`16:9`) |
| Upload behavior | Disabled by default; opt in per request or env |
| Upload target | `gdrive:guige-images` |
| Upload filename | `{topic-slug}-infographic-{YYYYMMDD}.png` |

## Assets

Always use the bundled character asset:

```text
assets/guige.jpeg
```

At run time, copy it into the output directory:

```text
infographic/{topic-slug}/refs/01-ref-guige.jpeg
```

Use the image as a style/character reference whenever the active image backend supports reference images. If the backend does not support reference images, inject the character traits in text:

- Q-style young male narrator
- sleepy half-lidded eyes
- mildly sarcastic / 吐槽 expression
- orange headband with Chinese text `鬼哥`
- blue hoodie
- acoustic guitar as a signature prop
- cute, efficient cartoon style: simple silhouette, readable pose, expressive face, no unnecessary detail
- may use Japanese manga-style expression effects when they fit the content: sweat drop, surprise lines, angry vein mark, speech bubble, speed lines, sparkle eyes, deadpan face, tiny chibi reaction sticker
- choose expressions based on the module content: surprise for key insights, sweat drop for risks, sparkle for opportunities, deadpan for obvious product friction, speed lines for action items
- used as a narrator, sticker, pointer, or callout host
- supportive visual role, never overpowering the information architecture

## Supported Layouts And Styles

Read [layouts-and-styles.md](references/layouts-and-styles.md) when choosing or explaining design options.

Before asking the user to choose parameters, print the Chinese quick-pick list from the `## 中文参数速查` section in [layouts-and-styles.md](references/layouts-and-styles.md).

Default recommendation:

```text
dense-modules + guige-journal + landscape + zh
```

Use the default when the user asks for 高密度信息大图, wants a social/shareable infographic, or does not specify visual preferences.

## Options

Accept CLI-style options in the user's request. Explicit options override defaults and should become the leading recommendation.

| Option | Values |
|--------|--------|
| `--layout` | Any layout in [layouts-and-styles.md](references/layouts-and-styles.md), e.g. `dense-modules`, `bento-dashboard`, `technical-map`, `linear-progression`, `comparison-matrix`, `hub-spoke`, `dashboard`, `circular-flow` |
| `--style` | Any style in [layouts-and-styles.md](references/layouts-and-styles.md), e.g. `guige-journal`, `lab-notes`, `social-pop`, `clean-explainer`, `hand-drawn-edu`, `pop-laboratory`, `technical-schematic`, `retro-pop-grid` |
| `--aspect` | Named: `portrait` (`9:16`), `landscape` (`16:9`), `square` (`1:1`). Custom W:H ratios are allowed, e.g. `3:4`, `4:3`, `2.35:1` |
| `--lang` | Output language for infographic text, e.g. `zh`, `en`, `ja`, `ko`, or another language code/name |
| `--upload` | Upload final image to Google Drive after generation |
| `--no-upload` | Force local-only delivery even if `GUIGE_INFOGRAPHIC_UPLOAD=1` |
| `--no-confirm` | Skip Step 4 confirmation |

Parameter handling:

- If `--layout`, `--style`, `--aspect`, or `--lang` is provided, use it in `analysis.md`, `structured-content.md`, and `prompts/infographic.md`.
- If only some options are provided, ask for confirmation only on the missing choices unless `--no-confirm` is present.
- If a provided layout/style is unknown, map it to the closest supported option and state the mapping before generation.
- `--lang` controls infographic text labels and body copy. Keep the headband text `鬼哥` unchanged as part of the character brand.
- If the user provides no explicit options, print the full Chinese option list before Step 4 and ask the user to reply with IDs, e.g. `layout=L1 style=S1 aspect=A2 lang=G1`, or to provide CLI-style options.

## Workflow

### Step 1: Setup

1. Derive a short English `topic-slug` from the source title or topic, e.g. `gpt-5-5-overview`.
2. Parse any explicit options: `--layout`, `--style`, `--aspect`, `--lang`, `--upload`, `--no-upload`, `--no-confirm`.
3. Create:
   - `infographic/{topic-slug}/`
   - `infographic/{topic-slug}/refs/`
   - `infographic/{topic-slug}/prompts/`
4. If the output directory already exists, append `-YYYYMMDD-HHMMSS`.
5. Copy `assets/guige.jpeg` to `refs/01-ref-guige.jpeg`.
6. Save pasted content or source file content as `source-{topic-slug}.md`.

### Step 2: Analyze Content

Create `analysis.md` with:

- title
- topic
- source language and output language
- audience
- content type
- complexity
- selected or recommended layout/style/aspect/language
- 1-3 learning objectives
- key statistics and quotes copied exactly
- recommended layout/style/aspect combinations
- any user design instructions

Preserve factual data exactly. Strip secrets, credentials, API keys, and tokens if present.

### Step 3: Structure Content

Create `structured-content.md` with:

- title and subtitle
- overview
- 4-7 visual modules
- for each module: key concept, exact content points, visual treatment, text labels
- data points and quotes copied exactly
- Gui Ge character usage notes
- suggested Gui Ge expressions for key modules when helpful

Keep module text concise enough for image generation. Preserve source facts, but compress wording for display labels when necessary.

### Step 4: Confirm Options

Confirm before generating unless the user explicitly says `--no-confirm`, `直接生成`, `不用确认`, `跳过确认`, or equivalent.

Before asking, print a Chinese selection menu with:

- all supported layouts and one-line Chinese descriptions
- all supported styles and one-line Chinese descriptions
- aspect choices: `portrait`, `landscape`, `square`, or custom ratio
- language choices: `zh`, `en`, `ja`, `ko`, or custom language
- upload choices: local only by default, upload only when requested

Ask for:

- layout/style combination, unless both were supplied explicitly
- aspect ratio, unless supplied explicitly
- output language, only if source language differs from requested/user language and `--lang` is absent
- any must-include or must-remove points

Offer 3 options by default:

- `dense-modules + guige-journal + landscape + zh` as the default high-density Gui Ge infographic
- `bento-dashboard + guige-journal` for cleaner overview images
- `technical-map + lab-notes` for more technical/benchmark-heavy content

### Step 5: Generate Prompt

Read [prompt-template.md](references/prompt-template.md), then create:

```text
prompts/infographic.md
```

The prompt must include:

- chosen layout/style/aspect
- chosen output language
- full structured content
- all required text labels in the selected language
- `Gui Ge Character Reference` section
- reference frontmatter:

```yaml
references:
  - ref_id: 01
    filename: 01-ref-guige.jpeg
    usage: style
```

Write the prompt file before invoking any image backend.

### Step 6: Generate Image

Use the best image backend available in the current runtime:

1. Native runtime image tool, if available.
2. A configured local image generation skill or script, if the current runtime provides one.
3. If no image backend exists, stop and report the prepared prompt path.

If the backend supports image references, pass `refs/01-ref-guige.jpeg`. If not, rely on the text character section in the prompt.

Normalize final output to:

```text
infographic/{topic-slug}/infographic.png
```

If the backend saves to another path, copy the generated image to `infographic.png` and leave the original in place.

If `infographic.png` exists, rename the old file to:

```text
infographic-backup-YYYYMMDD-HHMMSS.png
```

### Step 7: Optional Google Drive Upload

Google Drive upload is optional and disabled by default.

Upload only when one of these is true:

- The user explicitly asks to upload, e.g. `上传到 Google Drive`, `传到 guige-images`, `upload to Drive`, or equivalent.
- The user passes `--upload`.
- The environment variable `GUIGE_INFOGRAPHIC_UPLOAD=1` is set.

Do not upload when the user passes `--no-upload`.

When upload is enabled and `infographic.png` exists, run:

```bash
guige-infographic/scripts/upload_to_drive.sh \
  infographic/{topic-slug}/infographic.png \
  "{topic-slug}" \
  "gdrive:guige-images"
```

The upload script requires `rclone` configured with a Google Drive remote named `gdrive`.

If upload is not enabled, skip this step and report the local image path.

If upload is enabled but fails, keep the local image and report:

- local image path
- upload target
- exact upload error
- required fix, usually installing/configuring `rclone`

### Step 8: Final Report

Report:

- topic
- layout, style, aspect, language, image backend
- local image path
- Google Drive path, upload skipped, or upload blocker
- generated files: source, analysis, structured content, prompt

Keep the report short.

## Helper Scripts

Use [upload_to_drive.sh](scripts/upload_to_drive.sh) for Drive upload.

Environment overrides:

| Env var | Meaning |
|---------|---------|
| `GUIGE_INFOGRAPHIC_UPLOAD` | Set to `1` to upload by default |
| `GUIGE_IMAGES_TARGET` | Override upload target, e.g. `gdrive:guige-images` |
| `GUIGE_IMAGES_DATE` | Override date suffix for deterministic tests |
