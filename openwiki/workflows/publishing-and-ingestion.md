# Publishing and ingestion workflows

[← Quickstart](../quickstart.md) · [Architecture](../architecture/overview.md)

These skills cross service or account boundaries. Treat their `SKILL.md` safety gates, dry-run modes, and explicit user confirmation points as product behavior—not optional implementation detail.

## Workflow map

| Entry | Skill | Output / next hand-off |
|---|---|---|
| X/Twitter status or article URL | `guige-x-2-md` | Local Markdown, optional `imgs/` and `videos/` |
| Localized X content destined for article | `guige-x-to-blog` | External Hugo post and optional WeChat draft |
| YouTube/X/Twitter video URL | `guige-video-download` | Local media folder; optional Drive upload |
| Any generated material | `guige-drive-upload` | Configured `rclone` remote |
| Markdown, HTML, or text | `guige-to-wechat` | Rendered `.wechat.html` and/or official WeChat **draft** |
| Comic detail/list URL | root `scripts/download_to_drive.py` | Chapter PDFs uploaded through `rclone` |

## X/Twitter acquisition and republishing

`guige-x-2-md` uses a self-contained Python client for reverse-engineered X web APIs, not an official X API. It has a persistent, platform-specific consent gate and requires logged-in X cookies. Cookie resolution can use explicitly configured environment variables, a local cache, or the `--login` Chrome/Edge flow. Do not print cookie values, bypass the gate, or claim broad service reliability: the contract acknowledges breakage/account-restriction risk.

Default results are `x-to-markdown/{username-or-id}/{tweet-or-article-id}/{content-slug}.md`. `--download-media` stores media beside it and rewrites references; `--json` is the reliable hand-off format.

`guige-x-to-blog` is a human/agent workflow specification rather than an executable package. It invokes X-to-Markdown with localized media, applies the blog workflow, converts body images to WebP, and stops for a user-confirmed cover before publishing. It can hand the finished article to `guige-to-wechat`, but WeChat publication is optional and requires confirmation. Its documented target is a separate Hugo checkout; do not accidentally treat that checkout as part of this repository or commit temporary WeChat cover conversions there.

## Downloading authorized media

`guige-video-download` wraps `yt-dlp` for YouTube, Shorts, X, and Twitter. It can produce video/audio, cover, subtitles, metadata, `source-url.txt`, and `download-result.json` below `~/Downloads/guige-skill-video/{platform}/{author-or-channel}/{title-or-id}/`.

It explicitly supports only content the user is entitled to access/save. Do not alter it to bypass DRM, paid/private content, or platform controls. `--cookies-from-browser` passes the user’s own browser session to `yt-dlp` for normally accessible content; it is not a circumvention mechanism. `ffmpeg` is needed for many merge/audio paths. Tests are local logic tests, not network integration tests.

## Drive delivery

`guige-drive-upload` is the preferred reusable backend for new skill integrations. It uses `rclone`, with a typical configured remote named `gdrive:`. The default remote layout is:

```text
gdrive:guige-skills/{skill-name}/{task-folder}/
```

`--layout task` instead uses `{target}/{task-folder}`. It supports planning/structured results with `--dry-run` and `--json`. Upload is opt-in through a user request, a source workflow `--upload`, or `GUIGE_DRIVE_UPLOAD=1`; respect `--no-upload`. An upload failure should leave local files intact.

`guige-video-download` already invokes this CLI directly. Prefer that same interface for new producers rather than duplicating `rclone` logic. The root comic script is a deliberate exception: it independently converts downloaded chapters to PDFs and shells out to `rclone`, uploading PDFs only and deleting local cache after a successful upload. `--no-upload` keeps the PDFs. Recent history added configurable and built-in `jmpic` host fallback candidates; preserve retries/fallback behavior if touching it.

## WeChat drafts, not browser posting

`guige-to-wechat` uses the official Official Account API to render Markdown/HTML/text, upload inline images and cover material, and call `draft/add`. It creates a remote **draft**, not a browser-automated public post. `--dry-run --json` validates/renders without API calls and should be used for changes.

Credentials are selected locally from account-specific configuration or environment naming conventions; logs should identify only the chosen source/account label, never secret values. A cover is required. The skill may best-effort convert unsupported/oversized images with local `sips` or `cwebp`. Generated HTML is a sibling `*.wechat.html` file and is ignored by Git.

## Safe change checklist

1. Preserve consent/authorization requirements and noninteractive flags only for trusted explicit use.
2. Exercise `--dry-run` or `--json` before live X, Drive, WeChat, or download behavior.
3. Keep machine/account configuration out of repository outputs and test fixtures.
4. Update unit tests when changing URL parsing, path/slugging, payload formatting, or upload layout. See [Engineering guide](../engineering.md) for locations.
