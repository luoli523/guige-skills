---
name: guige-markdown-to-html
description: Convert Markdown files into styled, WeChat-friendly HTML and a publication manifest with metadata, cover selection, and resolved image assets. Use when the user asks to convert Markdown to HTML, render or prepare Markdown for WeChat, create a publisher-ready article package, or preview/export a rich-text article without publishing it.
---

# Gui Ge Markdown to HTML

Render a Markdown file into standalone HTML. This skill only renders content; it does not upload images, open browsers, or publish to any platform.

## Runtime

```bash
python3 {baseDir}/scripts/main.py <markdown-file> [options]
```

Use only this skill's scripts and configuration. Do not read or depend on another skill's private files or configuration.

## Configuration

Load the first existing file:

1. `.guige-skills/guige-markdown-to-html/EXTEND.md`
2. `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-markdown-to-html/EXTEND.md`
3. `$HOME/.guige-skills/guige-markdown-to-html/EXTEND.md`

Supported keys:

```yaml
default_theme: modern
default_color: blue
default_font_family: sans
default_font_size: 16
default_code_theme: monokai
mac_code_block: true
cite: true
keep_title: false
```

CLI arguments override `EXTEND.md`, which overrides skill defaults. Frontmatter supplies article metadata only.

## Usage

```bash
# Render article.md to article.html
python3 {baseDir}/scripts/main.py article.md

# Render with typography choices
python3 {baseDir}/scripts/main.py article.md \
  --theme grace --color '#009874' --font-family serif-cjk --font-size 16

# Produce the explicit HTML + manifest interface for a publisher
python3 {baseDir}/scripts/main.py article.md \
  --output article.html --manifest article.wechat.json --json
```

## Options

| Option | Description |
|---|---|
| `<markdown-file>` | Existing `.md` input file |
| `--output <path>` | Output HTML path; default is the input path with `.html` extension |
| `--theme <name>` | `default`, `simple`, `grace`, or `modern` |
| `--color <name-or-hex>` | Primary accent color |
| `--font-family <name-or-css>` | `sans`, `serif`, `serif-cjk`, `mono`, or a CSS font stack |
| `--font-size <px>` | Base font size from `14` to `18` |
| `--code-theme <name>` | Code-block style; `github` is light and `dark`, `github-dark`, `monokai`, and `nord` use a dark surface |
| `--no-mac-code-block` | Disable the mac-style code-block header |
| `--cite` | Convert ordinary external links into bottom citations |
| `--no-cite` | Keep ordinary external links inline |
| `--keep-title` | Keep the first H1/H2 in the HTML body |
| `--manifest <path>` | Write a schema version 1 renderer-to-publisher JSON manifest |
| `--dry-run` | Render and validate without writing output |
| `--json` | Print a machine-readable result |

## Rendering Rules

- Support headings, emphasis, inline and fenced code, blockquotes, lists, tables, rules, links, and images.
- Render styles inline for WeChat and rich-text-editor compatibility.
- Resolve `title`, `author`, and `description` / `summary` from frontmatter.
- Remove the first H1/H2 from the body by default. Keep it only with `--keep-title`.
- Preserve image `src` values and report each image with its source, resolved local path, and alt text. Resolve cover frontmatter (`coverImage`, `featureImage`, `cover`, `image`), then `imgs/cover.png`, then the first inline image.
- Convert ordinary external links to numbered bottom citations only with `--cite`. Keep WeChat article links inline.
- Treat raw HTML as unsupported input. Escape generated text.

## Output

Use `--json` to return a result similar to:

```json
{
  "success": true,
  "htmlPath": "/path/article.html",
  "title": "文章标题",
  "summary": "文章摘要",
  "author": "鬼哥",
  "schemaVersion": 1,
  "assetBaseDir": "/path",
  "cover": {
    "source": "cover.webp",
    "resolvedPath": "/path/cover.webp"
  },
  "theme": "grace",
  "color": "#009874",
  "codeTheme": "github",
  "contentImages": [
    {
      "source": "imgs/chart.png",
      "resolvedPath": "/path/imgs/chart.png",
      "alt": "图表"
    }
  ]
}
```

## Boundaries

- Do not publish, authenticate, call platform APIs, or open browsers.
- Do not mutate input Markdown files.
- Do not call `baoyu-*` skills or use their scripts or configuration.
- Treat the generated manifest as the public handoff to publisher skills.
- Add Mermaid only as an explicit future feature with a static PNG fallback and documented runtime dependency.
