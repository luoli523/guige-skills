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
