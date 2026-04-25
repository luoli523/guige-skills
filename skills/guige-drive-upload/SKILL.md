---
name: guige-drive-upload
description: Upload generated Gui Ge skill materials to Google Drive through rclone. Use after any guige-skills workflow creates images, prompts, markdown, PDFs, HTML, or output folders and the user asks to upload/share/save to Google Drive, or when GUIGE_DRIVE_UPLOAD=1 is set. Default Drive layout is guige-skills/<skill-name>/<task-folder>/all generated materials.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
        - rclone
---

# Gui Ge Drive Upload

Reusable Google Drive upload backend for Gui Ge skills.

This skill uploads generated materials using `rclone`. It is intentionally generic: other skills should generate their own files first, then call this skill for upload.

## Default Drive Layout

Upload all materials to:

```text
guige-skills/{skill-name}/{task-folder}/
```

Examples:

```text
guige-skills/guige-infographic/python-cli-pipeline/
guige-skills/guige-imagen/clean-keyboard-product-photo/
```

`task-folder` must be related to the current task. Derive it from the topic, title, image subject, or output folder name.

## Runtime

Main script:

```bash
python3 {baseDir}/scripts/main.py
```

The script uses only the Python standard library and shells out to `rclone`.

## First-Time Setup

Before uploading, verify `rclone` exists and has a Google Drive remote:

```bash
rclone version
rclone listremotes
```

If `rclone` is missing, install it:

```bash
brew install rclone
```

If no Google Drive remote exists, initialize one:

```bash
rclone config
```

Recommended interactive choices:

1. Choose `n` for New remote.
2. Name it `gdrive`.
3. Choose Google Drive as the storage provider.
4. Use the default client id/secret unless the user has their own Google OAuth app.
5. Choose normal access to their own Drive.
6. Complete browser authentication.
7. Confirm the remote, then verify:

```bash
rclone lsd gdrive:
```

Default upload target is:

```text
gdrive:
```

Uploads create the `guige-skills/` folder at the root of that Drive remote. To use another remote or base folder, set `GUIGE_DRIVE_TARGET` or pass `--target`.

## Usage

```bash
python3 {baseDir}/scripts/main.py \
  --skill guige-infographic \
  --task "python cli pipeline" \
  --paths ~/Downloads/guige-skill-imagen/python-cli-pipeline-infographic.png \
          infographic/python-cli-pipeline/analysis.md \
          infographic/python-cli-pipeline/structured-content.md \
          infographic/python-cli-pipeline/prompts/infographic.md
```

Upload a whole generated folder:

```bash
python3 {baseDir}/scripts/main.py \
  --skill guige-infographic \
  --task "python cli pipeline" \
  --paths infographic/python-cli-pipeline
```

JSON output:

```bash
python3 {baseDir}/scripts/main.py \
  --skill guige-imagen \
  --task "clean keyboard product photo" \
  --paths ~/Downloads/guige-skill-imagen/clean-keyboard-product-photo.png \
  --json
```

## Options

| Option | Description |
|--------|-------------|
| `--paths <paths...>` | Files or directories to upload. Required |
| `--skill <name>` | Source skill name, e.g. `guige-infographic`. Required |
| `--task <text>` | Task/topic/folder name. Required |
| `--target <remote>` | rclone remote root. Default: `GUIGE_DRIVE_TARGET` or `gdrive:` |
| `--dry-run` | Print planned uploads without running rclone |
| `--json` | Print JSON summary |

## Environment

| Env var | Meaning |
|---------|---------|
| `GUIGE_DRIVE_TARGET` | Default rclone target, e.g. `gdrive:` |
| `GUIGE_DRIVE_UPLOAD` | Set to `1` for skills to upload by default |

## Caller Guidance

Other skills should call this skill only when upload is enabled by user request, `--upload`, or `GUIGE_DRIVE_UPLOAD=1`. Respect `--no-upload` when the source skill supports it.

If upload fails, keep local files and report:

- local material paths
- intended Drive folder
- exact error
- likely fix, usually installing `rclone` or configuring the `gdrive` remote
