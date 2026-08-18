---
name: guige-markdown-to-html
description: Convert Markdown files into styled, WeChat-friendly HTML with inline CSS, frontmatter metadata, code blocks, tables, blockquotes, image manifests, and optional bottom citations for external links. Use when the user asks to convert Markdown to HTML, render Markdown for WeChat or a rich-text editor, create styled HTML from a .md file, or preview/export a WeChat-ready article without publishing it.
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
default_theme: default
default_color: blue
default_font_family: sans
default_font_size: 16
default_code_theme: github
mac_code_block: true
cite: false
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

# Return a machine-readable image manifest for a publisher
python3 {baseDir}/scripts/main.py article.md --cite --json --output article.wechat.html
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
| `--keep-title` | Keep the first H1/H2 in the HTML body |
| `--dry-run` | Render and validate without writing output |
| `--json` | Print a machine-readable result |

## Rendering Rules

- Support headings, emphasis, inline and fenced code, blockquotes, lists, tables, rules, links, and images.
- Render styles inline for WeChat and rich-text-editor compatibility.
- Resolve `title`, `author`, and `description` / `summary` from frontmatter.
- Remove the first H1/H2 from the body by default. Keep it only with `--keep-title`.
- Preserve image `src` values and report each image with its source, resolved local path, and alt text. Do not upload or download images.
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
- Add Mermaid only as an explicit future feature with a static PNG fallback and documented runtime dependency.
