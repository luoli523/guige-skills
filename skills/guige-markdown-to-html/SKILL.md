---
name: guige-markdown-to-html
description: Convert Markdown into reusable, styled HTML for the web, embedded fragments, email, or WeChat. Supports GFM, footnotes, alerts, math, code highlighting, diagrams, Obsidian images, configurable CSS and asset handling, and versioned JSON manifests. Use for Markdown-to-HTML conversion, HTML export, rich-text rendering, or publisher-ready HTML preparation; it renders files but does not publish them.
metadata:
  openclaw:
    requires:
      anyBins:
        - bun
        - npx
---

# Gui Ge Markdown to HTML

Render an existing Markdown file as general-purpose HTML. This skill owns conversion and local asset preparation only; it does not authenticate, open a browser for publication, or call a publishing API.

## Runtime

Resolve `${BUN_X}` as `bun` when installed, otherwise `npx -y bun`. If `scripts/node_modules` is absent, run `${BUN_X} install` in the scripts directory before conversion.

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown-file> [options]
```

Use only this skill's scripts and configuration. Do not read or invoke another skill's private implementation.

## Choose an Output Profile

Use `web` unless the requested destination requires another profile:

| Profile | Use for | Default CSS mode |
|---|---|---|
| `web` | Standalone HTML documents | `embedded` |
| `fragment` | HTML embedded in another application | `none` |
| `wechat` | WeChat-compatible rich text | `inline` |
| `email` | Email-oriented HTML | `inline` |
| `bare` | Semantic HTML with minimal presentation assumptions | `none` |

Read [profiles.md](references/profiles.md) when selecting a non-default profile or CSS delivery mode.

## Typical Commands

```bash
# Generic standalone web document
${BUN_X} {baseDir}/scripts/main.ts article.md

# Reusable HTML fragment
${BUN_X} {baseDir}/scripts/main.ts article.md --profile fragment --output article.fragment.html

# Portable single-file HTML with embedded images
${BUN_X} {baseDir}/scripts/main.ts article.md --assets embed

# General manifest v2
${BUN_X} {baseDir}/scripts/main.ts article.md --manifest article.json --manifest-version 2 --json

# Explicit compatibility handoff to guige-to-wechat
${BUN_X} {baseDir}/scripts/main.ts article.md --profile wechat \
  --manifest article.wechat.json --manifest-version 1 --json
```

Read [cli.md](references/cli.md) for all options and [manifest.md](references/manifest.md) when another tool consumes the output.

## Content Support

- CommonMark plus GFM tables, task lists, autolinks, and strikethrough
- headings, nested lists, blockquotes, links, images, and fenced code
- footnotes, GitHub-style alerts, and `{base|annotation}` ruby text
- inline and display math rendered as MathML
- syntax highlighting, optional line numbers, and Mac-style code headers
- Markdown images and Obsidian `![[image.png|alt]]` embeds
- Mermaid and PlantUML source fallback; optional local static SVG/PNG rendering

Read [extensions.md](references/extensions.md) only when the input uses math, diagrams, raw HTML, Obsidian embeds, or non-default asset handling.

## Configuration

Load the first existing `EXTEND.md`:

1. `.guige-skills/guige-markdown-to-html/EXTEND.md`
2. `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-markdown-to-html/EXTEND.md`
3. `$HOME/.guige-skills/guige-markdown-to-html/EXTEND.md`

CLI values override configuration, which overrides profile defaults. Configuration is private to this skill.

## Safety and Boundaries

- Raw HTML is escaped by default. `--allow-html` still sanitizes elements, attributes, and URL schemes.
- Remote images are fetched only with explicit `--assets download`; private-network targets, unsafe media types, and files over 20 MiB are rejected.
- Static diagram rendering is explicit. It invokes local `mmdc` or `plantuml` without a shell and falls back to source when unavailable.
- Never execute scripts embedded in Markdown or generated HTML.
- Do not mutate the input Markdown.
- Do not publish, upload to a platform, or read publisher credentials.
- Use manifest schema v2 for general integrations. Emit schema v1 only for the existing `guige-to-wechat` compatibility boundary.
