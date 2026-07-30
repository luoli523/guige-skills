from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

STATE_REL_PATH = Path("work") / "job-state.json"

# Keys that must never be persisted; guards against accidental leaks.
FORBIDDEN_SUBSTRINGS = ("api_key", "authorization", "x-api-key")


def default_state(task: str) -> dict[str, Any]:
    return {
        "task": task,
        "created_at": datetime.date.today().isoformat(),
        "minimax": {
            "source_file_id": None,
            "voice_id": None,
            "tts_model": "speech-2.8-hd",
            "full_audio": "work/voiceover-full.mp3",
            "preview_audio": "work/preview-15s.mp3",
        },
        "heygen": {
            "image_asset_id": None,
            "preview_audio_asset_id": None,
            "preview_video_id": None,
            "full_audio_asset_id": None,
            "full_video_id": None,
        },
        "status": {
            "narration": "not_started",
            "preview": "not_started",
            "approved_by_user": False,
            "final": "not_started",
        },
        "outputs": {
            "preview_video": "outputs/preview-15s.mp4",
            "final_video": None,
        },
    }


def state_path(task_dir: Path) -> Path:
    return task_dir / STATE_REL_PATH


def load_state(task_dir: Path) -> dict[str, Any]:
    path = state_path(task_dir)
    if not path.exists():
        raise SystemExit(f"no state file at {path}; run `init --task {task_dir.name}` first")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(task_dir: Path, state: dict[str, Any]) -> None:
    serialized = json.dumps(state, ensure_ascii=False, indent=2)
    lowered = serialized.lower()
    for marker in FORBIDDEN_SUBSTRINGS:
        if marker in lowered:
            raise SystemExit(f"refusing to save state containing '{marker}'")
    path = state_path(task_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized + "\n", encoding="utf-8")


def init_task(base_dir: Path, task: str) -> Path:
    task_dir = base_dir / task
    for sub in ("inputs", "work", "outputs"):
        (task_dir / sub).mkdir(parents=True, exist_ok=True)
    path = state_path(task_dir)
    if not path.exists():
        save_state(task_dir, default_state(task))
    return task_dir
