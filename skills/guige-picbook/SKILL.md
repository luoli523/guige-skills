---
name: guige-picbook
description: Generate children's educational picture books from a topic or source idea. Searches kid-friendly knowledge, adapts it with an LLM, writes structured Markdown chapters with illustration prompts and sources, and can optionally upload to NotebookLM to create Slides PDF, send the PDF to Telegram, or upload generated materials through guige-drive-upload. Use for 儿童绘本, 科普绘本, picture book, kids educational book, NotebookLM 绘本 slides, or turning a topic into a child-friendly illustrated reading script.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge Picbook

Generate child-friendly educational picture books from a topic. The skill uses its bundled Python runtime and self-managed environment under the `guige-skills` layout.

## Defaults

| Setting | Default |
|---------|---------|
| Language | `en` unless user asks otherwise |
| Age range | 8-12 |
| Pages/chapters | 30 |
| Illustration aspect ratio | `3:4` portrait |
| Working root | `picbook/{topic-slug}/` |
| Markdown | `picbook/{topic-slug}/{topic-slug}.md` |
| Slides | NotebookLM Slides enabled by default |
| Notebook name | `儿童绘本` |
| Upload | disabled unless `--upload` or `GUIGE_DRIVE_UPLOAD=1`; default target root is `drive:Rakuten Kobo/YYYYMM` |
| Python | 3.10+ |
| Environment | Self-managed `.venv/` under this skill |

## Runtime

Main script:

```bash
python3 skills/guige-picbook/scripts/main.py
```

If `python3` is older than 3.10, the launcher tries `python3.12`, `python3.11`, then `python3.10`.

The launcher self-initializes:

- creates `skills/guige-picbook/.venv/`
- prefers `uv` when available
- falls back to `python -m venv` + `pip`
- installs core requirements and NotebookLM requirements by default
- reinstalls when requirement files change

For configuration details, read [config.md](references/config.md). For NotebookLM behavior, read [notebooklm.md](references/notebooklm.md). For content quality guidance, read [style-guide.md](references/style-guide.md) when judging or revising generated books.

## Options

Accept CLI-style options in the user's request.

| Option | Description |
|--------|-------------|
| `--lang en\|zh\|ja\|ko` | Output language |
| `--chapters N` / `--pages N` | Page/chapter count, 3-30 |
| `--min-age N` / `--max-age N` | Target age range |
| `--slides` / `--no-slides` | Enable or skip NotebookLM Slides |
| `--nlm-instructions <text>` | NotebookLM custom slide prompt |
| `--nlm-format detailed\|presenter` | NotebookLM Slides format |
| `--nlm-length default\|short` | NotebookLM Slides length |
| `--telegram` | Send generated Slides PDF to Telegram |
| `--upload` | Upload generated folder through `guige-drive-upload` |
| `--output <file>` | Exact Markdown output file |
| `--output-dir <dir>` | Root directory for default output path |

## Workflow

1. Derive or accept a concrete topic. Prefer specific topics like `恐龙`, `太阳系`, `how music boxes work`; ask for clarification only if the topic is too broad to produce a coherent child-facing book.
2. Choose language, age range, and page/chapter count from the request. If absent, use defaults.
3. Run:

```bash
python3 skills/guige-picbook/scripts/main.py generate "{topic}" \
  --lang zh \
  --pages 30 \
  --min-age 8 \
  --max-age 12
```

4. Use `--no-slides` when the user only wants the Markdown book or NotebookLM is unavailable.
5. Use `--upload` only when the user asks to upload/share/save to Google Drive, or when `GUIGE_DRIVE_UPLOAD=1` is present.
   By default, upload target root is `drive:Rakuten Kobo/YYYYMM`, where `YYYYMM` is the runtime year and month, for example `drive:Rakuten Kobo/202605`. Each book is uploaded into its topic folder under that monthly root.

NotebookLM dependencies are installed and validated by default even when a run uses `--no-slides`. If NotebookLM dependency setup fails, report the setup failure. If Slides generation fails, the command must fail after keeping the Markdown file.

The generator searches Tavily, SerpAPI, and Wikipedia when configured, then uses the selected LLM provider to write the book. If search APIs are not configured, Wikipedia and LLM fallback still allow generation.

## Commands

Prepare the self-managed environment:

```bash
python3 skills/guige-picbook/scripts/main.py setup
```

Run diagnostics:

```bash
python3 skills/guige-picbook/scripts/main.py doctor
```

Remove the self-managed environment:

```bash
python3 skills/guige-picbook/scripts/main.py clean-env
```

Generate Markdown only:

```bash
python3 skills/guige-picbook/scripts/main.py generate "恐龙" --lang zh --no-slides
```

Generate Markdown + NotebookLM Slides:

```bash
python3 skills/guige-picbook/scripts/main.py generate "太阳系" --lang zh --slides
```

Upload an existing Markdown book to NotebookLM:

```bash
python3 skills/guige-picbook/scripts/main.py upload-to-notebooklm picbook/solar-system/solar-system.md
```

Generate Slides from an existing NotebookLM URL or ID:

```bash
python3 skills/guige-picbook/scripts/main.py generate-slides "https://notebooklm.google.com/notebook/..."
```

Send an existing Slides PDF:

```bash
python3 skills/guige-picbook/scripts/main.py share picbook/solar-system/solar-system_slides.pdf --telegram
```

## Output Rules

- Keep generated materials under `picbook/{topic-slug}/` unless the user provides `--output`.
- Do not store secrets in generated files.
- Preserve Markdown and prompt-source traceability: final books should include title, topic, target age, summary, pages/chapters, illustration prompts, knowledge points, and references.
- If NotebookLM fails, keep the Markdown result and report the failure reason.
- If upload fails, keep local files and report the intended upload action.

## Dependencies And Login

NotebookLM Slides require:

```bash
notebooklm login
```

This opens a browser for Google authentication. If the runtime cannot open a browser or lacks NotebookLM credentials, use `--no-slides`; dependency installation still includes NotebookLM by default.

## Validation

For code changes to this skill, run:

```bash
python3 -m pytest skills/guige-picbook/scripts/tests
```

For a no-network smoke test, run only commands that do not call LLM/search services:

```bash
python3 skills/guige-picbook/scripts/main.py languages
python3 skills/guige-picbook/scripts/main.py version
```
