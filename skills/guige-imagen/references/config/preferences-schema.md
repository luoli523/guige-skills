---
name: preferences-schema
description: EXTEND.md YAML schema for guige-imagen preferences
---

# Preferences Schema

`guige-imagen` reads a small YAML frontmatter subset. Keep values simple: strings, nulls, and the `default_model` map.

## Full Schema

```yaml
---
version: 1

default_provider: null      # google|openai|null
default_quality: null       # normal|2k|null
default_aspect_ratio: null  # "16:9"|"1:1"|"4:3"|"3:4"|"9:16"|null
default_image_size: null    # 1K|2K|4K|null

default_model:
  openai: null              # e.g. "gpt-image-1.5"
  google: null              # e.g. "gemini-3-pro-image-preview"
---
```

## Minimal Example

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

## Paths

First hit wins:

```text
<cwd>/.guige-skills/guige-imagen/EXTEND.md
${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-imagen/EXTEND.md
$HOME/.guige-skills/guige-imagen/EXTEND.md
```
