---
name: guige-x-2-md
description: Convert X/Twitter tweets, threads, and X Articles to Markdown using a Python reverse-engineered X API client. Use when the user provides x.com/twitter.com status or article URLs, asks to save tweets, archive X threads, convert X to Markdown, or download tweet media locally.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge X to Markdown

Convert X/Twitter content to local Markdown:

- Tweet/status URLs -> thread-aware Markdown with YAML front matter
- X Article URLs -> article body, media, referenced tweets, and YAML front matter
- Optional media localization -> `imgs/` and `videos/` next to the Markdown file

This skill intentionally mirrors `baoyu-danger-x-to-markdown`, but the implementation is Python and self-contained in this repository.

## Safety Gate

This skill uses reverse-engineered X web APIs, not the official X API. Before any conversion:

1. Check the consent file:
   - macOS: `~/Library/Application Support/guige-skills/x-2-md/consent.json`
   - Linux: `${XDG_DATA_HOME:-~/.local/share}/guige-skills/x-2-md/consent.json`
   - Windows: `%APPDATA%/guige-skills/x-2-md/consent.json`
2. If it contains `accepted: true` and `disclaimerVersion: "1.0"`, print the warning and proceed.
3. Otherwise show the disclaimer and ask the user to accept. If declined, stop.

The Python script enforces this consent gate.

## Runtime

Main script:

```bash
python3 {baseDir}/scripts/main.py <url>
```

No third-party Python packages are required.

## Authentication

The script needs logged-in X cookies. It resolves them in this order:

1. Environment variables: `X_AUTH_TOKEN`, `X_CT0`, optional `X_GUEST_TOKEN`, `X_TWID`
2. Cached cookie file under the Gui Ge data directory
3. Chrome/Edge DevTools fallback opened by `--login` or automatically when cookies are missing

Useful environment variables:

| Env var | Meaning |
|---------|---------|
| `X_AUTH_TOKEN` | X `auth_token` cookie |
| `X_CT0` | X `ct0` CSRF cookie |
| `X_BEARER_TOKEN` | Override web bearer token |
| `X_USER_AGENT` | Override request user-agent |
| `X_CHROME_PATH` | Override Chrome/Edge executable |
| `X_DATA_DIR` | Override data directory |
| `X_COOKIE_PATH` | Override cookie file path |
| `X_CHROME_PROFILE_DIR` | Override Chrome profile directory |

## Usage

```bash
# Save a tweet/thread to ./x-to-markdown/{username}/{tweet-id}/{slug}.md
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890

# Save to a specific file or output directory
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 -o output.md
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 -o ./archive/

# X Article
python3 skills/guige-x-2-md/scripts/main.py https://x.com/i/article/1234567890

# Download media locally and rewrite Markdown links
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 --download-media

# Machine-readable result
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 --json

# Refresh cookies only
python3 skills/guige-x-2-md/scripts/main.py --login
```

## Options

| Option | Description |
|--------|-------------|
| `<url>` | `x.com`/`twitter.com` status URL or `x.com/i/article/<id>` |
| `--url <url>` | URL as named option |
| `-o, --output <path>` | Output file or directory |
| `--json` | Print JSON summary |
| `--download-media` | Download images/videos to local `imgs/` and `videos/` |
| `--login` | Open Chrome/Edge to refresh cookies and exit |
| `--accept-risk` | Non-interactive consent acceptance for trusted local use |

## Output

Default output path:

```text
x-to-markdown/{username-or-id}/{tweet-or-article-id}/{content-slug}.md
```

Markdown front matter includes source URL, requested URL, author fields for tweets, tweet count, and cover image when available.

When `--download-media` is enabled:

- Image files are saved under `imgs/`
- Video files are saved under `videos/`
- Markdown links and `coverImage` front matter are rewritten to local relative paths

## Workflow For Agents

1. Confirm the user has authorized reverse-engineered X API usage. The script also enforces this.
2. Run `--login` first if the user has not provided `X_AUTH_TOKEN` and `X_CT0`.
3. Convert the URL with `--json` when you need robust path reporting.
4. If the user asks for local media, pass `--download-media`.
5. Report the saved Markdown path and any media directories.

If X changes its web API, the script may fail. Preserve the error text; it usually identifies whether cookies, query IDs, or network access are the issue.
