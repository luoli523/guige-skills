---
name: guige-to-wechat
description: Publish a guige-markdown-to-html render manifest to a WeChat Official Account draft through the official API. Use when the user asks to publish a prepared article to 微信公众号, post to WeChat, create a WeChat draft, upload a WeChat cover or inline images, or manage WeChat draft settings.
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge To WeChat

Publish a prepared render manifest to a WeChat Official Account draft. This skill is the publishing channel only: it does not parse Markdown, render HTML, choose typography, or generate article metadata.

First create the HTML and manifest with `guige-markdown-to-html`, then pass the manifest here.

## Runtime

```bash
python3 {baseDir}/scripts/main.py <render-manifest.json> [options]
```

The script uses only Python's standard library. It uploads local or remote images through the official API. JPEG and PNG assets are uploaded unchanged; WebP and other unsupported assets are converted to JPEG with local `sips` or ImageMagick when available. Oversized body images are also resized to meet WeChat's limit.

## Render Manifest Contract

`guige-markdown-to-html` is a general renderer. Resolve `${BUN_X}` as `bun` when installed, otherwise `npx -y bun`, then use its explicit `wechat` profile and schema version 1 compatibility manifest for this publisher:

```bash
${BUN_X} <markdown-to-html-baseDir>/scripts/main.ts article.md \
  --profile wechat --output article.html \
  --manifest article.wechat.json --manifest-version 1
```

The publisher requires:

```json
{
  "schemaVersion": 1,
  "htmlPath": "/absolute/path/article.html",
  "assetBaseDir": "/absolute/path",
  "title": "文章标题",
  "summary": "文章摘要",
  "author": "鬼哥",
  "contentSourceUrl": "https://luoli523.github.io/p/article-slug/",
  "cover": {"source": "cover.webp", "resolvedPath": "/absolute/path/cover.webp"},
  "contentImages": [
    {"source": "chart.webp", "resolvedPath": "/absolute/path/chart.webp", "alt": "图表"}
  ]
}
```

The manifest is the explicit interface between skills. Do not import or read another skill's scripts or configuration.

## Configuration

Load preferences from the first existing file:

1. `.guige-skills/guige-to-wechat/EXTEND.md`
2. `${XDG_CONFIG_HOME:-$HOME/.config}/guige-skills/guige-to-wechat/EXTEND.md`
3. `$HOME/.guige-skills/guige-to-wechat/EXTEND.md`

Legacy Baoyu paths remain a credential migration fallback when no Gui Ge configuration exists.

```yaml
need_open_comment: 1
only_fans_can_comment: 0

accounts:
  - name: 鬼哥
    alias: guige
    default: true
    app_id: wx...
    app_secret: ...
```

Credentials resolve from the selected account, account-specific environment variables (such as `WECHAT_GUIGE_APP_ID`), generic `WECHAT_APP_ID` / `WECHAT_APP_SECRET`, then supported `.env` files.

## Usage

```bash
# 1. Render Markdown and write its schema v1 publication manifest
${BUN_X} <markdown-to-html-baseDir>/scripts/main.ts article.md \
  --profile wechat --output article.html \
  --manifest article.wechat.json --manifest-version 1

# 2. Validate the draft inputs without API calls
python3 {baseDir}/scripts/main.py article.wechat.json --dry-run --json

# 3. Publish a normal article draft
python3 {baseDir}/scripts/main.py article.wechat.json --account guige

# Publish an image-news draft or override only this publication's cover
python3 {baseDir}/scripts/main.py article.wechat.json --type newspic
python3 {baseDir}/scripts/main.py article.wechat.json --cover cover.jpg
```

## Options

| Option | Description |
|--------|-------------|
| `<render-manifest.json>` | Schema version 1 manifest from `guige-markdown-to-html` |
| `--type news|newspic` | Draft article type; default `news` |
| `--cover <path-or-url>` | Override the manifest cover for this publication |
| `--account <alias>` | Select a configured WeChat account |
| `--dry-run` | Validate manifest, cover, images, and draft inputs without API calls |
| `--output-html <path>` | Save HTML after WeChat image URLs are substituted |
| `--json` | Print machine-readable output |

## Channel Responsibilities

- Obtain the access token and apply account/comment settings.
- Upload inline images through `media/uploadimg` and replace their HTML URLs.
- Upload the cover through `material/add_material`; convert WebP covers to JPEG first while leaving JPEG/PNG covers unchanged.
- Build and submit the `draft/add` request for `news` or `newspic`.
- Send manifest `author` as the original author and `contentSourceUrl` as the `news` article's “阅读原文” link.
- Preserve a final HTML copy after image URL substitution.

The official draft API does not expose the editor's “创作来源” setting, so this skill leaves that setting for manual configuration in the WeChat backend.

After a successful publish, manage the draft at `https://mp.weixin.qq.com` → 内容管理 → 草稿箱.
