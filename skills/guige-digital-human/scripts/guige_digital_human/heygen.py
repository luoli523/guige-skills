from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .env import require_env
from .http import download_file, post_json, request_json, upload_multipart

DEFAULT_BASE_URL = "https://api.heygen.com"
POLL_INTERVAL_SECONDS = 15
POLL_TIMEOUT_SECONDS = 30 * 60


def _base_url() -> str:
    return os.environ.get("HEYGEN_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _headers() -> dict[str, str]:
    return {"x-api-key": require_env("HEYGEN_API_KEY", "HeyGen API key")}


def upload_asset(path: Path) -> str:
    result = upload_multipart(f"{_base_url()}/v3/assets", path, headers=_headers())
    data = result.get("data", result)
    asset_id = data.get("asset_id") or data.get("id")
    if not asset_id:
        raise SystemExit(f"HeyGen asset upload returned no asset_id: {result}")
    return str(asset_id)


def create_video(
    image_asset_id: str, audio_asset_id: str, resolution: str = "720p"
) -> str:
    result = post_json(
        f"{_base_url()}/v3/videos",
        {
            "type": "image",
            "image": {"type": "asset_id", "asset_id": image_asset_id},
            "audio_asset_id": audio_asset_id,
            "resolution": resolution,
        },
        headers=_headers(),
    )
    data = result.get("data", result)
    video_id = data.get("video_id") or data.get("id")
    if not video_id:
        raise SystemExit(f"HeyGen video creation returned no video_id: {result}")
    return str(video_id)


def get_video(video_id: str) -> dict[str, Any]:
    result = request_json(f"{_base_url()}/v3/videos/{video_id}", headers=_headers())
    return result.get("data", result)


def poll_video(video_id: str) -> dict[str, Any]:
    """Poll until completed/failed; raises on timeout with resume hint."""
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while True:
        data = get_video(video_id)
        status = str(data.get("status", "")).lower()
        if status == "completed":
            return data
        if status == "failed":
            raise SystemExit(
                f"HeyGen video {video_id} failed: {data.get('failure_message', 'unknown reason')}"
            )
        if time.monotonic() > deadline:
            raise SystemExit(
                f"polling timed out for video {video_id}; the job may still be running — "
                f"rerun the same command later to resume polling"
            )
        time.sleep(POLL_INTERVAL_SECONDS)


def decode_check(video_path: Path) -> bool:
    """Full-file decode check via ffmpeg; True means the MP4 decodes cleanly."""
    if not shutil.which("ffmpeg"):
        return video_path.stat().st_size > 0
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video_path), "-f", "null", "-"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode == 0 and not result.stderr.strip()


def generate_video(
    task_dir: Path,
    state: dict[str, Any],
    stage: str,
    resolution: str,
) -> dict[str, Any]:
    """Run one HeyGen stage ('preview' or 'final'): upload assets, create, poll, download."""
    hg = state["heygen"]

    if not hg.get("image_asset_id"):
        portrait = None
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = task_dir / "inputs" / f"portrait{ext}"
            if candidate.exists():
                portrait = candidate
                break
        if portrait is None:
            raise SystemExit(f"no portrait under {task_dir}/inputs/")
        hg["image_asset_id"] = upload_asset(portrait)

    audio_key = f"{stage}_audio_asset_id"
    video_key = f"{stage}_video_id"
    audio_rel = state["minimax"]["preview_audio" if stage == "preview" else "full_audio"]
    audio_path = task_dir / audio_rel
    if not audio_path.exists():
        raise SystemExit(f"missing narration audio {audio_path}; run `narrate` first")

    if not hg.get(audio_key):
        hg[audio_key] = upload_asset(audio_path)
    if not hg.get(video_key):
        hg[video_key] = create_video(hg["image_asset_id"], hg[audio_key], resolution)

    data = poll_video(hg[video_key])
    video_url = data.get("video_url") or data.get("url")
    if not video_url:
        raise SystemExit(f"completed video {hg[video_key]} has no video_url")

    out_name = "preview-15s.mp4" if stage == "preview" else "final-1080p.mp4"
    out_path = task_dir / "outputs" / out_name
    download_file(video_url, out_path)
    if not decode_check(out_path):
        raise SystemExit(f"decode check failed for {out_path}; retry download before regenerating")

    state["status"][stage] = "completed"
    if stage == "final":
        state["outputs"]["final_video"] = f"outputs/{out_name}"
    return state
