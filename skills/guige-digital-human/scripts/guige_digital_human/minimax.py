from __future__ import annotations

import datetime
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .env import require_env
from .http import post_json, upload_multipart

DEFAULT_BASE_URL = "https://api.minimax.io"
DEFAULT_TTS_MODEL = "speech-2.8-hd"
PREVIEW_SECONDS = 15


def _base_url() -> str:
    return os.environ.get("MINIMAX_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _auth() -> tuple[str, str]:
    api_key = require_env("MINIMAX_API_KEY", "MiniMax API key")
    group_id = require_env("MINIMAX_GROUP_ID", "MiniMax GroupId")
    return api_key, group_id


def upload_voice_source(voice_path: Path) -> str:
    api_key, group_id = _auth()
    result = upload_multipart(
        f"{_base_url()}/v1/files/upload?GroupId={group_id}",
        voice_path,
        headers={"Authorization": f"Bearer {api_key}"},
        fields={"purpose": "voice_clone"},
    )
    file_id = result.get("file", {}).get("file_id") or result.get("file_id")
    if not file_id:
        raise SystemExit(f"MiniMax upload returned no file_id: {result}")
    return str(file_id)


def make_voice_id(task: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "", task) or "voice"
    return f"guige{slug}{datetime.date.today().strftime('%Y%m%d')}"


def clone_voice(file_id: str, voice_id: str) -> str:
    api_key, group_id = _auth()
    result = post_json(
        f"{_base_url()}/v1/voice_clone?GroupId={group_id}",
        {"file_id": file_id, "voice_id": voice_id},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    base = result.get("base_resp", {})
    if base.get("status_code") not in (0, None):
        raise SystemExit(f"MiniMax voice_clone failed: {base}")
    return voice_id


def synthesize(text: str, voice_id: str, out_path: Path, speed: float = 1.0) -> None:
    api_key, group_id = _auth()
    model = os.environ.get("MINIMAX_TTS_MODEL", DEFAULT_TTS_MODEL)
    result = post_json(
        f"{_base_url()}/v1/t2a_v2?GroupId={group_id}",
        {
            "model": model,
            "text": text,
            "voice_setting": {"voice_id": voice_id, "speed": speed},
            "audio_setting": {"format": "mp3"},
        },
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=600,
    )
    base = result.get("base_resp", {})
    if base.get("status_code") not in (0, None):
        raise SystemExit(f"MiniMax t2a_v2 failed: {base}")
    audio_hex = result.get("data", {}).get("audio")
    if not audio_hex:
        raise SystemExit(f"MiniMax t2a_v2 returned no audio data: keys={list(result)}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(bytes.fromhex(audio_hex))


def cut_preview(full_audio: Path, preview_audio: Path, seconds: int = PREVIEW_SECONDS) -> bool:
    """Cut the first N seconds with ffmpeg; False when ffmpeg is unavailable."""
    if not shutil.which("ffmpeg"):
        return False
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(full_audio),
            "-t",
            str(seconds),
            "-c",
            "copy",
            str(preview_audio),
        ],
        check=True,
        timeout=120,
    )
    return True


def read_script_text(script_path: Path) -> str:
    text = script_path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"script is empty: {script_path}")
    return text


def narrate(task_dir: Path, state: dict[str, Any], speed: float = 1.0) -> dict[str, Any]:
    """Full narration stage: upload -> clone -> synthesize -> cut preview."""
    voice = None
    for ext in (".mp3", ".m4a", ".wav"):
        candidate = task_dir / "inputs" / f"voice-source{ext}"
        if candidate.exists():
            voice = candidate
            break
    if voice is None:
        raise SystemExit(f"no voice sample under {task_dir}/inputs/")

    mm = state["minimax"]
    if not mm.get("source_file_id"):
        mm["source_file_id"] = upload_voice_source(voice)
    if not mm.get("voice_id"):
        mm["voice_id"] = clone_voice(mm["source_file_id"], make_voice_id(state["task"]))

    script_text = read_script_text(task_dir / "inputs" / "script.md")
    full_audio = task_dir / mm["full_audio"]
    synthesize(script_text, mm["voice_id"], full_audio, speed=speed)

    preview_audio = task_dir / mm["preview_audio"]
    if not cut_preview(full_audio, preview_audio):
        # Without ffmpeg fall back to the full audio as preview source.
        shutil.copyfile(full_audio, preview_audio)
    state["status"]["narration"] = "completed"
    return state
