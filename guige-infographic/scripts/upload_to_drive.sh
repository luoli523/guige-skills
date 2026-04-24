#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: upload_to_drive.sh <image-path> <topic-slug> [target]

Uploads an infographic image to Google Drive via rclone.

Defaults:
  target: ${GUIGE_IMAGES_TARGET:-gdrive:guige-images}
  filename: <topic-slug>-infographic-YYYYMMDD.png
EOF
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage
  exit 64
fi

image_path="$1"
topic_slug="$2"
target="${3:-${GUIGE_IMAGES_TARGET:-gdrive:guige-images}}"
date_suffix="${GUIGE_IMAGES_DATE:-$(date +%Y%m%d)}"

if [[ ! -f "$image_path" ]]; then
  echo "Error: image not found: $image_path" >&2
  exit 66
fi

if ! command -v rclone >/dev/null 2>&1; then
  echo "Error: rclone is not installed or not on PATH." >&2
  echo "Install rclone and configure a Google Drive remote named 'gdrive'." >&2
  exit 69
fi

safe_slug="$(
  printf '%s' "$topic_slug" |
    tr '[:upper:]' '[:lower:]' |
    sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
)"

if [[ -z "$safe_slug" ]]; then
  safe_slug="guige-infographic"
fi

filename="${safe_slug}-infographic-${date_suffix}.png"
destination="${target%/}/${filename}"

rclone copyto "$image_path" "$destination"

printf '%s\n' "$destination"
