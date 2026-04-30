---
name: guige-imagen
description: Image generation foundation for Gui Ge skills. Uses the bundled Python API backend with OpenAI or Google when guige-scoped API keys are configured or deterministic local output is required; when no API key is configured, Codex sessions should prefer Codex's built-in imagen/image generation tool before other runtime tools. Supports provider/model selection, aspect ratio, size, quality, JSON output, and Gui Ge scoped EXTEND.md/.env configuration. Use when the user asks to generate, create, draw, render, or edit images through the guige-skills image backend.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge Imagen

Image generation foundation for the Gui Ge skill set.

This skill is a generic backend. It does not apply Gui Ge character style by default; upstream skills such as `guige-infographic` should provide their own prompt, reference images, and output conventions.

## Backend Selection

Use the best image backend available for the user's context:

1. Python API backend, when guige-scoped API keys are configured or deterministic local output is required.
2. If no guige-scoped API key is configured and the session is running in Codex, use Codex's built-in imagen/image generation tool first.
3. If no guige-scoped API key is configured and the session is not running in Codex, try the native image generation tool provided by the current interactive runtime.
4. If no API backend or native runtime image tool exists, write or report the prepared prompt and explain the missing backend.

The native runtime image tool is not called by `scripts/main.py`; it is a skill-layer fallback. Codex's built-in imagen/image generation tool is the preferred no-key fallback only when the skill is being used inside Codex. The Python backend is the stable automation path for workflows that need repeatable CLI behavior or future batch generation.

All generated images should end up in:

```text
~/Downloads/guige-skill-imagen/
```

Use a content-related filename derived from the image topic or prompt, for example:

```text
~/Downloads/guige-skill-imagen/python-cli-pipeline.png
```

If the target filename already exists, append a numeric suffix such as `-2`.

## Python Backend

Main script:

```bash
python3 {baseDir}/scripts/main.py
```

The v0.1 runtime uses only the Python standard library.

The Python backend requires at least one provider API key. Codex/ChatGPT login state does not automatically grant API access to this script. When no guige-scoped API key is configured, do not run the Python backend as the first choice in Codex; use Codex's built-in imagen/image generation tool instead.

## Supported Providers

| Provider | Env key | Default model |
|----------|---------|---------------|
| `openai` | `OPENAI_API_KEY` | `gpt-image-1.5` |
| `google` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` | `gemini-3-pro-image-preview` |

Provider base URL overrides:

| Provider | Env key |
|----------|---------|
| OpenAI | `OPENAI_BASE_URL` |
| Google | `GOOGLE_BASE_URL` |

Model overrides:

| Provider | Env key |
|----------|---------|
| OpenAI | `OPENAI_IMAGE_MODEL` |
| Google | `GOOGLE_IMAGE_MODEL` |

## Configuration

Load priority:

```text
CLI args > EXTEND.md > <cwd>/.guige-skills/.env > ~/.guige-skills/.env > non-provider process env > built-in defaults
```

Provider environment variables are guige-scoped by default. The Python backend ignores ambient shell values for `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, provider base URLs, and provider model env overrides unless they are defined in `.guige-skills/.env`.

To deliberately use provider values already exported in the shell, set this in the shell for that run. This control flag is not loaded from `.guige-skills/.env`.

```bash
GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1
```

`EXTEND.md` paths, first hit wins:

| Path | Scope |
|------|-------|
| `.guige-skills/guige-imagen/EXTEND.md` | Project |
| `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-imagen/EXTEND.md` | XDG |
| `$HOME/.guige-skills/guige-imagen/EXTEND.md` | User home |

Schema: [preferences-schema.md](references/config/preferences-schema.md).

Never read, write, source, or rely on `.baoyu-skills`.

## Usage

Use these examples when choosing the Python API backend.

```bash
# Basic; saves to ~/Downloads/guige-skill-imagen/cat.png
python3 {baseDir}/scripts/main.py --prompt "A cat"

# Force provider/model; --image is only an extension hint
python3 {baseDir}/scripts/main.py --prompt "A cat" --image cat.png --provider openai --model gpt-image-1.5

# Google with aspect ratio and quality
python3 {baseDir}/scripts/main.py --prompt "A landscape" --image out.png --provider google --ar 16:9 --quality 2k

# Prompt from files
python3 {baseDir}/scripts/main.py --promptfiles system.md content.md --image out.png

# Reference images
python3 {baseDir}/scripts/main.py --prompt "Restyle this image" --ref source.png --image out.png --provider google

# JSON output
python3 {baseDir}/scripts/main.py --prompt "A cat" --image cat.png --json
```

More examples: [usage-examples.md](references/usage-examples.md).

## Options

| Option | Description |
|--------|-------------|
| `--prompt <text>`, `-p` | Prompt text |
| `--promptfiles <files...>` | Read prompt from files and concatenate with blank lines |
| `--image <path>` | Optional filename/extension hint. Final image is still saved under `~/Downloads/guige-skill-imagen/` with a content-related filename |
| `--provider openai\|google` | Force provider |
| `--model <id>`, `-m` | Provider model ID |
| `--ar <ratio>` | Aspect ratio, e.g. `16:9`, `1:1`, `4:3`, `9:16` |
| `--size <WxH>` | Provider-specific pixel size, e.g. `1024x1024` |
| `--quality normal\|2k` | Quality preset; default is `2k` |
| `--imageSize 1K\|2K\|4K` | Google image size hint |
| `--ref <files...>` | Reference images |
| `--n <count>` | Number of images requested from provider; v0.1 saves the first returned image |
| `--json` | Print JSON result |

## Provider Notes

Read only when needed:

- OpenAI: [openai.md](references/providers/openai.md)
- Google: [google.md](references/providers/google.md)

## Current Scope

v0.1 intentionally excludes batch generation, retries, and provider concurrency controls. Add those after the single-image path is stable.
