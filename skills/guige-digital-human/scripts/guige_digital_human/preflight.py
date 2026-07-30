from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

VOICE_EXTENSIONS = {".mp3", ".m4a", ".wav"}
PORTRAIT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
VOICE_MAX_BYTES = 20 * 1024 * 1024
HEYGEN_UPLOAD_MAX_BYTES = 32 * 1024 * 1024
VOICE_MIN_SECONDS = 10
VOICE_MAX_SECONDS = 5 * 60


def find_input(task_dir: Path, stem: str, extensions: set[str]) -> Path | None:
    inputs = task_dir / "inputs"
    for ext in sorted(extensions):
        candidate = inputs / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def probe_duration_seconds(path: Path) -> float | None:
    """Best-effort duration via ffprobe; None when unavailable."""
    if not shutil.which("ffprobe"):
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return None


def check_assets(task_dir: Path) -> list[str]:
    """Return a list of problems; empty list means preflight passed."""
    problems: list[str] = []

    script = task_dir / "inputs" / "script.md"
    if not script.exists():
        problems.append(f"missing script: {script}")
    elif not script.read_text(encoding="utf-8").strip():
        problems.append(f"script is empty: {script}")

    portrait = find_input(task_dir, "portrait", PORTRAIT_EXTENSIONS)
    if portrait is None:
        problems.append(f"missing portrait: {task_dir}/inputs/portrait.(png|jpg|jpeg)")
    elif portrait.stat().st_size > HEYGEN_UPLOAD_MAX_BYTES:
        problems.append(f"portrait exceeds HeyGen 32MB upload limit: {portrait}")

    voice = find_input(task_dir, "voice-source", VOICE_EXTENSIONS)
    if voice is None:
        problems.append(f"missing voice sample: {task_dir}/inputs/voice-source.(mp3|m4a|wav)")
    else:
        size = voice.stat().st_size
        if size > VOICE_MAX_BYTES:
            problems.append(f"voice sample exceeds MiniMax 20MB limit: {voice} ({size} bytes)")
        duration = probe_duration_seconds(voice)
        if duration is not None and not VOICE_MIN_SECONDS <= duration <= VOICE_MAX_SECONDS:
            problems.append(
                f"voice sample duration {duration:.1f}s outside MiniMax 10s-5min range: {voice}"
            )

    return problems
