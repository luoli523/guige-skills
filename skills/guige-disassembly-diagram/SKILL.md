---
name: guige-disassembly-diagram
description: Generate high-quality Chinese teaching explainer images for object teardown, exploded views, cutaway views, internal structure diagrams, product anatomy cards, component labels, material callouts, and working-principle flowcharts. Use when the user asks for 拆解图, 爆炸图, 剖面图, 半剖视图, 产品结构说明图, 科普海报, 知识卡片, or a text-to-image prompt/image about an item's exterior, internals, parts, materials, and operating logic. Uses guige-imagen or the current runtime image backend for final generation.
---

# Gui Ge Disassembly Diagram

Create a clean Chinese educational teardown image for one object, device, machine, product, organism part, or technical system. The output should look like a polished technology explainer poster / product anatomy card, with clear Simplified Chinese labels and readable information hierarchy.

This skill is a high-level prompt workflow. Use `guige-imagen` for the image-generation backend when keyed or deterministic output is needed; in no-key Codex sessions, prefer the built-in image generation tool.

## Defaults

| Setting | Default |
|---------|---------|
| Language | `zh` unless user asks otherwise |
| Working root | `disassembly-diagram/{topic-slug}/` |
| Final image directory | `~/Downloads/guige-skill-imagen/` |
| Final image filename | `{topic-slug}-disassembly-diagram.png` |
| Default aspect | `landscape` (`16:9`) |
| Default style | modern technical education infographic |
| Upload behavior | Disabled by default; opt in per request or env |
| Upload backend | `guige-drive-upload` |
| Upload Drive folder | `guige-skills/guige-disassembly-diagram/{topic-slug}/` |

## Options

Accept CLI-style options in the user's request.

| Option | Values |
|--------|--------|
| `--aspect` | `landscape` (`16:9`), `portrait` (`9:16`), `square` (`1:1`), `4:3`, or custom ratio |
| `--lang` | Output label language, default `zh` |
| `--mode` | `auto`, `exploded`, `cutaway`, `hybrid`; default `hybrid` |
| `--upload` | Upload final image and materials to Google Drive |
| `--no-upload` | Force local-only delivery even if `GUIGE_DRIVE_UPLOAD=1` |
| `--no-confirm` | Skip confirmation |

Mode handling:

- `hybrid`: show exterior, exploded layers, cutaway, detail callouts, and principle flow. Use this by default.
- `exploded`: emphasize parts, assembly order, and connection relationships.
- `cutaway`: emphasize internal layout, section view, channels, circuits, mechanical paths, or fluid paths.
- `auto`: choose the most useful mode from the object type.

## Workflow

### Step 1: Setup

1. Identify the target object from the user request. Replace placeholder text such as `{……}` with the concrete topic.
2. Derive a short English `topic-slug`.
3. Parse explicit options: `--aspect`, `--lang`, `--mode`, `--upload`, `--no-upload`, `--no-confirm`.
4. Create:
   - `disassembly-diagram/{topic-slug}/`
   - `disassembly-diagram/{topic-slug}/prompts/`
5. If the output directory already exists, append `-YYYYMMDD-HHMMSS`.
6. Save the user's topic, constraints, and source material as `source-{topic-slug}.md`.

### Step 2: Analyze Structure

Create `analysis.md` with:

- title and target object
- audience and intended use
- selected aspect, language, and mode
- exterior features to show
- likely internal structures and component groups
- material categories to distinguish, such as metal, plastic, glass, rubber, ceramic, fabric, composite, fluid, electronic module
- working-principle sequence
- uncertainty notes

For a specific model, branded product, medical device, safety-critical equipment, weapon, or other high-stakes object, ground the structure in user-provided source material or an authoritative reference before presenting exact internals. If the exact internal design is unknown, label the output as a schematic explainer instead of claiming exact teardown accuracy.

### Step 3: Structure The Card

Create `structured-content.md` with concise Chinese content:

- title and optional subtitle
- 5-8 primary external/internal labels
- 3-6 exploded-view component labels
- 3-5 local detail callouts, each with a short explanation
- 4-6 functional modules with one-line roles
- 4-6 working-principle flow nodes, connected by arrows
- material/color rendering notes

Keep labels short enough for image generation. Prefer clear terms like `外壳`, `密封圈`, `控制芯片`, `传感器`, `电机`, `齿轮组`, `散热片`, `接口`, `电池`, `滤芯`, `支架`, `导流通道`.

### Step 4: Confirm

Confirm before generating unless the user explicitly says `--no-confirm`, `直接生成`, `不用确认`, `跳过确认`, or equivalent.

If confirmation is needed, ask for:

- aspect ratio, default `landscape`
- mode, default `hybrid`
- whether to prioritize exact technical realism or more poster-like communication
- any must-include or must-avoid parts

### Step 5: Generate Prompt

Read [prompt-template.md](references/prompt-template.md), then create:

```text
prompts/disassembly-diagram.md
```

Fill in:

- target object
- selected aspect, language, and mode
- structured content
- required labels and flow text
- accuracy/uncertainty note when relevant

The prompt must explicitly require:

- clear Simplified Chinese typography
- no garbled Chinese, no overlapping text, no tiny unreadable labels
- exterior view, exploded/cutaway structure, local magnifications, material cues, function area, and workflow arrows when mode allows
- clean white, light gray, or light blue-gray background

### Step 6: Generate Image

Use the best image backend available in the current runtime:

1. `guige-imagen` Python API backend, when guige-scoped API keys are configured or deterministic local output is required.
2. If no guige-scoped API key is configured and the session is running in Codex, use Codex's built-in image generation tool first.
3. If no guige-scoped API key is configured and the session is not running in Codex, try the native image generation tool provided by the current interactive runtime.
4. Another configured local image generation skill or script, if available.
5. If no image backend exists, stop and report the prepared prompt path.

Normalize final output by copying or moving the generated image to:

```text
~/Downloads/guige-skill-imagen/{topic-slug}-disassembly-diagram.png
```

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
  --skill guige-disassembly-diagram \
  --task "{topic-slug}" \
  --paths \
    ~/Downloads/guige-skill-imagen/{topic-slug}-disassembly-diagram.png \
    disassembly-diagram/{topic-slug}/source-{topic-slug}.md \
    disassembly-diagram/{topic-slug}/analysis.md \
    disassembly-diagram/{topic-slug}/structured-content.md \
    disassembly-diagram/{topic-slug}/prompts/disassembly-diagram.md
```

### Step 8: Final Report

Report:

- topic
- mode, aspect, language, image backend
- local final image path
- Google Drive path, upload skipped, or upload blocker
- generated files: source, analysis, structured content, prompt

Keep the report short.
