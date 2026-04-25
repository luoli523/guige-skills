#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_TARGET = "gdrive:"


@dataclass
class UploadItem:
    source: str
    destination: str
    is_dir: bool


@dataclass
class UploadPlan:
    target_root: str
    drive_folder: str
    items: list[UploadItem]


def slugify(value: str, fallback: str = "materials", max_length: int = 96) -> str:
    chars: list[str] = []
    previous_separator = False

    for char in value.casefold():
        if char.isalnum():
            chars.append(char)
            previous_separator = False
        elif not previous_separator:
            chars.append("-")
            previous_separator = True

    slug = "".join(chars).strip("-") or fallback
    if len(slug) <= max_length:
        return slug
    truncated = slug[:max_length].rstrip("-")
    if "-" in truncated:
        truncated = truncated.rsplit("-", 1)[0]
    return truncated or fallback


def normalize_target(value: str) -> str:
    return value.rstrip("/")


def join_remote(*parts: str) -> str:
    if not parts:
        return ""
    first, *rest = parts
    result = first.rstrip("/")
    for part in rest:
        cleaned = part.strip("/")
        if cleaned:
            separator = "" if result.endswith(":") else "/"
            result = f"{result}{separator}{cleaned}"
    return result


def resolve_existing_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    return path


def build_upload_plan(paths: list[str], skill: str, task: str, target: str) -> UploadPlan:
    if not paths:
        raise ValueError("--paths is required")
    skill_slug = slugify(skill, "skill")
    task_slug = slugify(task, "task")
    target_root = normalize_target(target)
    drive_folder = join_remote(target_root, "guige-skills", skill_slug, task_slug)

    items: list[UploadItem] = []
    for raw_path in paths:
        source = resolve_existing_path(raw_path)
        if source.is_dir():
            destination = join_remote(drive_folder, source.name)
            items.append(UploadItem(str(source), destination, True))
        else:
            destination = join_remote(drive_folder, source.name)
            items.append(UploadItem(str(source), destination, False))

    return UploadPlan(target_root, drive_folder, items)


def ensure_rclone() -> None:
    if shutil.which("rclone") is None:
        raise RuntimeError(
            "rclone is not installed or not on PATH. Install rclone and configure a Google Drive remote."
        )


def run_upload(plan: UploadPlan, dry_run: bool = False) -> None:
    if dry_run:
        return

    ensure_rclone()
    for item in plan.items:
        command = ["rclone", "copyto", item.source, item.destination]
        if item.is_dir:
            command = ["rclone", "copy", item.source, item.destination]
        subprocess.run(command, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-drive-upload",
        description="Upload generated Gui Ge skill materials to Google Drive through rclone.",
    )
    parser.add_argument("--paths", nargs="+", required=True, help="Files or directories to upload")
    parser.add_argument("--skill", required=True, help="Source skill name, e.g. guige-infographic")
    parser.add_argument("--task", required=True, help="Task/topic/folder name")
    parser.add_argument(
        "--target",
        default=os.environ.get("GUIGE_DRIVE_TARGET", DEFAULT_TARGET),
        help="rclone remote root, default: GUIGE_DRIVE_TARGET or gdrive:",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print plan without uploading")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        plan = build_upload_plan(args.paths, args.skill, args.task, args.target)
        run_upload(plan, args.dry_run)
        if args.json_output:
            print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
        else:
            print(plan.drive_folder)
        return 0
    except subprocess.CalledProcessError as error:
        print(f"Error: rclone failed with exit code {error.returncode}", file=sys.stderr)
        return error.returncode or 1
    except Exception as error:
        if args.json_output:
            print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
