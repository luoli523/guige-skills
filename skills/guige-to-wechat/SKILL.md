---
name: guige-to-wechat
description: Publish Markdown, HTML, or plain text to WeChat Official Account drafts using a Python API client. Use when the user asks to publish to 微信公众号, post to WeChat, create a WeChat draft, convert Markdown to WeChat-ready HTML, or upload article images/cover through the WeChat API.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge To WeChat

Publish articles to WeChat Official Account drafts through the official API.

This is a Python rewrite of the API article path from `baoyu-post-to-wechat`. It intentionally focuses on the stable API workflow:

- Markdown / HTML / plain text input
- Markdown frontmatter extraction
- WeChat-friendly HTML rendering
- Local/remote inline image upload through `media/uploadimg`
- Cover upload through `material/add_material`
- `draft/add` creation with comment controls
- JSON and dry-run output

Browser automation and image-text paste posting are not included in this Python version.

## Runtime

```bash
python3 {baseDir}/scripts/main.py <file-or-text>
```

The script uses only the Python standard library. If a body image is unsupported or larger than WeChat's body-image limit, it will best-effort convert/compress through local tools such as `sips` or `cwebp` when available.

## Configuration

Load preferences from the first existing file:

1. `.guige-skills/guige-to-wechat/EXTEND.md`
2. `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-to-wechat/EXTEND.md`
3. `$HOME/.guige-skills/guige-to-wechat/EXTEND.md`

For compatibility, the script also falls back to existing `baoyu-post-to-wechat` config paths when no Gui Ge config exists.

Supported keys:

```yaml
default_theme: default
default_color: blue
default_author: 鬼哥
need_open_comment: 1
only_fans_can_comment: 0

accounts:
  - name: 鬼哥
    alias: guige
    default: true
    app_id: wx...
    app_secret: ...
```

Credentials are resolved in this order:

1. Account `app_id` / `app_secret` in `EXTEND.md`
2. Prefixed env or env file keys when `--account <alias>` is used, e.g. `WECHAT_GUIGE_APP_ID`
3. Generic env vars `WECHAT_APP_ID` / `WECHAT_APP_SECRET`
4. Project `.guige-skills/.env`
5. User `~/.guige-skills/.env`
6. Compatibility fallback: `.baoyu-skills/.env` and `~/.baoyu-skills/.env`

## Usage

```bash
# Publish a Markdown article to draft
python3 skills/guige-to-wechat/scripts/main.py article.md --cover cover.webp

# Render and validate without API calls
python3 skills/guige-to-wechat/scripts/main.py article.md --cover cover.webp --dry-run --json

# HTML input
python3 skills/guige-to-wechat/scripts/main.py article.html --title "标题" --summary "摘要" --cover cover.jpg

# Plain text input; saves a Markdown file first
python3 skills/guige-to-wechat/scripts/main.py "这是一段要发布到公众号的内容" --title "标题" --cover cover.jpg

# Select account and style
python3 skills/guige-to-wechat/scripts/main.py article.md --account guige --theme simple --color teal

# Disable bottom citations for ordinary external links
python3 skills/guige-to-wechat/scripts/main.py article.md --no-cite --cover cover.jpg
```

## Options

| Option | Description |
|--------|-------------|
| `<file-or-text>` | Markdown file, HTML file, or plain text |
| `--type news|newspic` | Draft article type. Default: `news` |
| `--title <text>` | Override title |
| `--author <name>` | Override author |
| `--summary <text>` | Override digest/summary |
| `--cover <path-or-url>` | Cover image. Required for `news` unless first inline image can be used |
| `--theme <name>` | `default`, `simple`, `grace`, or `modern` |
| `--color <name-or-hex>` | Primary accent color |
| `--account <alias>` | Select account from `EXTEND.md` |
| `--no-cite` | Keep normal external links inline |
| `--dry-run` | Render and validate only |
| `--output-html <path>` | Save rendered/final HTML to a path |
| `--json` | Print machine-readable result |

## Markdown Fields

Frontmatter keys:

```yaml
---
title: "文章标题"
description: "摘要"
author: "鬼哥"
image: cover.webp
---
```

Cover fallback order:

1. `--cover`
2. frontmatter `coverImage`, `featureImage`, `cover`, or `image`
3. `imgs/cover.png`
4. first inline image in the article

Markdown external links are converted to bottom citations by default for WeChat-friendly output. Use `--no-cite` only when inline links are explicitly desired.

## Output

Successful API publish returns JSON similar to:

```json
{
  "success": true,
  "media_id": "...",
  "title": "...",
  "articleType": "news",
  "htmlPath": "article.wechat.html"
}
```

After publishing, manage drafts at `https://mp.weixin.qq.com` -> 内容管理 -> 草稿箱.
