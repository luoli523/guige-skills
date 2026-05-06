---
name: guige-video-download
description: Download videos, audio, thumbnails, subtitles, and metadata from YouTube, YouTube Shorts, X.com, and Twitter URLs using a self-contained Gui Ge workflow around yt-dlp. Use when the user asks to download/save/grab YouTube videos, X/Twitter videos, video thumbnails, audio-only files, subtitles, or upload downloaded video assets to Drive.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
        - yt-dlp
---

# Gui Ge Video Download

Download videos, audio, thumbnails, subtitles, and metadata from YouTube and X/Twitter URLs.

This skill is self-contained in `guige-skills`. Do not depend on, read from, or invoke any `baoyu-*` skill, config, environment file, or script.

## Safety Boundary

Use this skill only for content the user has rights to access and download, such as public videos, their own content, or content they are authorized to save.

Do not use it to bypass DRM, paid access, private account restrictions, platform permissions, or other access controls. Browser cookies may be used only for content the user can normally access in their own browser session.

## Runtime

Main script:

```bash
python3 {baseDir}/scripts/main.py <url>
```

The script uses Python standard library plus the external `yt-dlp` binary. `ffmpeg` is recommended for high-quality stream merging and audio conversion.

## Supported URLs

- YouTube watch URLs: `https://www.youtube.com/watch?v=...`
- YouTube short URLs: `https://youtu.be/...`
- YouTube Shorts: `https://www.youtube.com/shorts/...`
- X/Twitter status URLs: `https://x.com/<user>/status/<id>`
- Twitter status URLs: `https://twitter.com/<user>/status/<id>`

## Default Output

Local files are saved under:

```text
~/Downloads/guige-skill-video/{platform}/{author-or-channel}/{title-or-id}/
```

Each task writes `source-url.txt` and `download-result.json`. Depending on options, the directory may also contain `video.*`, `audio.*`, thumbnails, subtitle files, and `*.info.json`.

## Options

| Option | Description |
|--------|-------------|
| `<url...>` | One or more YouTube/X/Twitter URLs |
| `--quality best\|2160p\|1440p\|1080p\|720p\|480p\|360p\|audio` | Video quality cap or audio-only alias |
| `--format mp4\|webm\|mkv` | Video container, default `mp4` |
| `--audio-only` | Download audio only |
| `--audio-format mp3\|m4a\|wav\|opus` | Audio output format, default `m4a` |
| `--thumbnail` / `--no-thumbnail` | Download thumbnail; enabled by default |
| `--thumbnail-only` | Download metadata and thumbnail without video/audio |
| `--metadata` / `--no-metadata` | Write yt-dlp info JSON; enabled by default |
| `--subtitles` | Download subtitles and automatic subtitles when available |
| `--languages <codes>` | Subtitle language priority, comma-separated, e.g. `zh,en,ja` |
| `--cookies-from-browser <browser>` | Pass browser cookies to yt-dlp, e.g. `chrome`, `safari`, `firefox` |
| `--output-dir <dir>` | Override base output directory |
| `--upload` | Upload generated task folders through `guige-drive-upload` |
| `--no-upload` | Force local-only delivery even if `GUIGE_DRIVE_UPLOAD=1` |
| `--dry-run` | Print planned commands without downloading |
| `--json` | Print machine-readable JSON result |

For format selector details, read [yt-dlp-formats.md](references/yt-dlp-formats.md) only when changing script behavior.
For common failures, read [troubleshooting.md](references/troubleshooting.md).

## Usage

```bash
# Default: best available video as MP4, plus metadata and thumbnail
python3 {baseDir}/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --json

# Download a 1080p cap
python3 {baseDir}/scripts/main.py 'https://youtu.be/VIDEO_ID' --quality 1080p

# Download audio only
python3 {baseDir}/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --audio-only --audio-format mp3

# Download X/Twitter video using the user's browser session
python3 {baseDir}/scripts/main.py 'https://x.com/user/status/123' --cookies-from-browser chrome

# Download subtitles
python3 {baseDir}/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --subtitles --languages zh,en

# Upload output folder to Google Drive
python3 {baseDir}/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --upload --json
```

Always single-quote URLs in shell commands because `?` and `&` can be interpreted by shells.

## Workflow For Agents

1. Parse the user's requested URL(s), quality, output mode, subtitle needs, and upload preference.
2. Use `--cookies-from-browser` only when the user asks for it or when yt-dlp reports login/access is required and the user can access the content in their browser.
3. Run the script with `--json` for reliable path reporting.
4. If `--upload` is enabled, the script invokes `guige-drive-upload` and reports the Drive folder.
5. Report the local output folder and any Drive folder. Keep error text if a platform blocks access.

## Upload

Upload is disabled by default. It runs only when:

- the user explicitly asks to upload,
- `--upload` is passed,
- or `GUIGE_DRIVE_UPLOAD=1` is set.

`--no-upload` disables upload even when the environment variable is set.

The upload backend writes to:

```text
gdrive:guige-skills/guige-video-download/{task-folder}/
```
