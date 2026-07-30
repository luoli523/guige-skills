from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import heygen, minimax, preflight, state as state_mod
from .env import load_env_files

DEFAULT_BASE_DIR = Path("digital-human")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-digital-human",
        description="MiniMax voice clone + HeyGen Image-to-Video digital-human pipeline",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=DEFAULT_BASE_DIR,
        help="base directory holding task folders (default: digital-human/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("init", "create task directories and a fresh job-state.json"),
        ("preflight", "validate script/portrait/voice assets before paid API calls"),
        ("narrate", "MiniMax: upload voice, clone, synthesize narration + 15s preview"),
        ("preview", "HeyGen: generate 720p 15-second preview video"),
        ("approve", "record explicit user approval of the preview"),
        ("final", "HeyGen: generate full 1080p video (requires approval)"),
        ("status", "print job-state.json"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--task", required=True, help="task slug under the base directory")
        if name == "narrate":
            p.add_argument(
                "--speed",
                type=float,
                default=1.0,
                help="TTS speed, 0.95-1.05 recommended for Chinese lip sync",
            )
        if name == "final":
            p.add_argument(
                "--resolution", default="1080p", help="output resolution (default 1080p)"
            )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_env_files()
    task_dir = args.base_dir / args.task

    if args.command == "init":
        state_mod.init_task(args.base_dir, args.task)
        print(f"initialized {task_dir}")
        return 0

    if args.command == "preflight":
        problems = preflight.check_assets(task_dir)
        if problems:
            for p in problems:
                print(f"FAIL {p}")
            return 1
        print("preflight passed")
        return 0

    state = state_mod.load_state(task_dir)

    if args.command == "status":
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    if args.command == "narrate":
        state = minimax.narrate(task_dir, state, speed=args.speed)
        state_mod.save_state(task_dir, state)
        print(f"narration done: {task_dir / state['minimax']['full_audio']}")
        return 0

    if args.command == "preview":
        if state["status"]["narration"] != "completed":
            raise SystemExit("narration not completed; run `narrate` first")
        state["status"]["preview"] = "in_progress"
        state_mod.save_state(task_dir, state)
        state = heygen.generate_video(task_dir, state, stage="preview", resolution="720p")
        state_mod.save_state(task_dir, state)
        print(f"preview done: {task_dir / 'outputs' / 'preview-15s.mp4'}")
        print("review the preview and run `approve` before generating the final video")
        return 0

    if args.command == "approve":
        if state["status"]["preview"] != "completed":
            raise SystemExit("preview not completed; nothing to approve")
        state["status"]["approved_by_user"] = True
        state_mod.save_state(task_dir, state)
        print("approval recorded")
        return 0

    if args.command == "final":
        if not state["status"]["approved_by_user"]:
            raise SystemExit(
                "preview not approved; review outputs/preview-15s.mp4 and run `approve` first"
            )
        state["status"]["final"] = "in_progress"
        state_mod.save_state(task_dir, state)
        state = heygen.generate_video(task_dir, state, stage="final", resolution=args.resolution)
        state_mod.save_state(task_dir, state)
        print(f"final done: {task_dir / state['outputs']['final_video']}")
        return 0

    raise SystemExit(f"unknown command: {args.command}")
