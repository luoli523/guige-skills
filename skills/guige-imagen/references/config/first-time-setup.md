# First-Time Setup

`guige-imagen` does not create configuration interactively in v0.1. Create the files manually when defaults are useful.

## API Keys

Project-local:

```text
.guige-skills/.env
```

User-wide:

```text
~/.guige-skills/.env
```

Example:

```dotenv
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_IMAGE_MODEL=gemini-3-pro-image-preview
OPENAI_IMAGE_MODEL=gpt-image-1.5
```

The Python backend ignores provider values that are only present in the shell environment by default. Put provider API keys, base URLs, and model env overrides in one of the `.guige-skills/.env` files above.

If no guige-scoped API key is configured, `scripts/main.py` cannot call provider APIs. In Codex sessions, use Codex's built-in imagen/image generation tool as the first fallback; in non-Codex interactive sessions, try that runtime's native image generation tool before reporting that no backend is available.

To deliberately use already-exported shell provider values, set this in the shell for that run. This control flag is not loaded from `.guige-skills/.env`.

```bash
GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1
```

## Preferences

Project-local:

```text
.guige-skills/guige-imagen/EXTEND.md
```

Example:

```yaml
---
version: 1
default_provider: google
default_quality: 2k
default_aspect_ratio: "16:9"
default_model:
  google: "gemini-3-pro-image-preview"
  openai: "gpt-image-1.5"
---
```
