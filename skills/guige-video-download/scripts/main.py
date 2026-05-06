#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("~/Downloads/guige-skill-video").expanduser()
QUALITY_CHOICES = ("best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "audio")
VIDEO_FORMAT_CHOICES = ("mp4", "webm", "mkv")
AUDIO_FORMAT_CHOICES = ("mp3", "m4a", "wav", "opus")


class DownloadError(RuntimeError):
    pass


@dataclass
class DownloadPlan:
    url: str
    platform: str
    output_dir: str
    command: list[str]
    metadata_command: list[str] = field(default_factory=list)
    upload_enabled: bool = False


@dataclass
class DownloadResult:
    url: str
    platform: str
    output_dir: str
    files: list[str]
    metadata: dict[str, Any]
    command: list[str]
    dry_run: bool = False
    upload: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)


def slugify(value: str, fallback: str = "item", max_length: int = 96) -> str:
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


def identify_platform(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host in {"youtube.com", "m.youtube.com", "youtu.be", "youtube-nocookie.com"}:
        return "youtube"
    if host in {"x.com", "twitter.com", "mobile.twitter.com"}:
        return "x"
    return slugify(host or "video", "video", 32)


def extract_url_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "v" in query and query["v"]:
        return slugify(query["v"][0], "video", 64)
    parts = [part for part in parsed.path.split("/") if part]
    if "status" in parts:
        index = parts.index("status")
        if index + 1 < len(parts):
            return slugify(parts[index + 1], "status", 64)
    if parts:
        return slugify(parts[-1], "video", 64)
    return "video"


def parse_quality_height(quality: str) -> int | None:
    if quality == "best" or quality == "audio":
        return None
    match = re.fullmatch(r"(\d+)p", quality)
    if not match:
        raise ValueError(f"Unsupported quality: {quality}")
    return int(match.group(1))


def build_format_selector(quality: str, video_format: str, audio_only: bool = False) -> str:
    if audio_only or quality == "audio":
        return "bestaudio/best"

    height = parse_quality_height(quality)
    height_filter = f"[height<={height}]" if height else ""

    if video_format == "mp4":
        return (
            f"bv*{height_filter}[ext=mp4]+ba[ext=m4a]/"
            f"b{height_filter}[ext=mp4]/"
            f"bv*{height_filter}+ba/"
            f"b{height_filter}/best"
        )
    if video_format == "webm":
        return (
            f"bv*{height_filter}[ext=webm]+ba[ext=webm]/"
            f"bv*{height_filter}[ext=webm]+ba[ext=opus]/"
            f"b{height_filter}[ext=webm]/"
            f"bv*{height_filter}+ba/"
            f"b{height_filter}/best"
        )
    if video_format == "mkv":
        return f"bv*{height_filter}+ba/b{height_filter}/best"
    raise ValueError(f"Unsupported format: {video_format}")


def require_yt_dlp(dry_run: bool = False) -> str:
    executable = shutil.which("yt-dlp")
    if executable is None:
        if dry_run:
            return "yt-dlp"
        raise DownloadError("yt-dlp is not installed or not on PATH. Install it with `brew install yt-dlp`.")
    return executable


def ffmpeg_warning(args: argparse.Namespace) -> str | None:
    needs_ffmpeg = args.audio_only or args.quality != "best" or args.format in {"mp4", "webm", "mkv"}
    if needs_ffmpeg and shutil.which("ffmpeg") is None:
        return "ffmpeg is not on PATH; stream merging or audio conversion may fail."
    return None


def run_json_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "yt-dlp metadata command failed"
        raise DownloadError(message)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise DownloadError(f"yt-dlp returned invalid JSON: {error}") from error


def build_metadata_command(executable: str, url: str, args: argparse.Namespace) -> list[str]:
    command = [executable, "--dump-single-json", "--skip-download", "--no-playlist"]
    if args.cookies_from_browser:
        command.extend(["--cookies-from-browser", args.cookies_from_browser])
    command.append(url)
    return command


def metadata_summary(metadata: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "title",
        "uploader",
        "channel",
        "channel_id",
        "duration",
        "upload_date",
        "webpage_url",
        "extractor_key",
        "resolution",
        "ext",
    )
    return {key: metadata.get(key) for key in keys if metadata.get(key) is not None}


def output_dir_for(url: str, metadata: dict[str, Any] | None, base_dir: Path) -> Path:
    platform = identify_platform(url)
    if metadata:
        author = metadata.get("uploader") or metadata.get("channel") or metadata.get("creator") or platform
        title = metadata.get("title") or metadata.get("id") or extract_url_id(url)
        video_id = metadata.get("id") or extract_url_id(url)
        item = f"{title}-{video_id}" if video_id and video_id not in str(title) else str(title)
    else:
        author = platform
        item = extract_url_id(url)
    return base_dir / platform / slugify(str(author), platform) / slugify(str(item), "video")


def build_download_command(executable: str, url: str, output_dir: Path, args: argparse.Namespace) -> list[str]:
    audio_only = args.audio_only or args.quality == "audio"
    command = [executable, "--no-playlist", "--newline", "-P", str(output_dir)]

    if args.cookies_from_browser:
        command.extend(["--cookies-from-browser", args.cookies_from_browser])

    if args.thumbnail:
        command.append("--write-thumbnail")
    if args.metadata:
        command.append("--write-info-json")
    if args.subtitles:
        command.extend(["--write-subs", "--write-auto-subs"])
        if args.languages:
            command.extend(["--sub-langs", args.languages])

    if args.thumbnail_only:
        command.extend(["--skip-download", "-o", "thumbnail.%(ext)s"])
    elif audio_only:
        command.extend(
            [
                "-f",
                build_format_selector(args.quality, args.format, audio_only=True),
                "-x",
                "--audio-format",
                args.audio_format,
                "-o",
                "audio.%(ext)s",
            ]
        )
    else:
        command.extend(
            [
                "-f",
                build_format_selector(args.quality, args.format),
                "--merge-output-format",
                args.format,
                "-o",
                "video.%(ext)s",
            ]
        )

    command.append(url)
    return command


def list_files(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    files = [path.relative_to(output_dir).as_posix() for path in output_dir.rglob("*") if path.is_file()]
    return sorted(files)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_result(output_dir: Path, result: DownloadResult) -> None:
    path = output_dir / "download-result.json"
    path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def upload_output(output_dir: Path, task: str) -> dict[str, Any]:
    upload_script = repo_root() / "skills" / "guige-drive-upload" / "scripts" / "main.py"
    command = [
        sys.executable,
        str(upload_script),
        "--skill",
        "guige-video-download",
        "--task",
        task,
        "--paths",
        str(output_dir),
        "--json",
    ]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "guige-drive-upload failed"
        raise DownloadError(message)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"output": completed.stdout.strip()}


def should_upload(args: argparse.Namespace) -> bool:
    if args.no_upload:
        return False
    if args.upload:
        return True
    return os.environ.get("GUIGE_DRIVE_UPLOAD") == "1"


def process_url(url: str, args: argparse.Namespace) -> DownloadResult:
    executable = require_yt_dlp(args.dry_run)
    platform = identify_platform(url)
    base_dir = Path(args.output_dir).expanduser().resolve()
    warnings = [warning for warning in [ffmpeg_warning(args)] if warning]

    metadata_command = build_metadata_command(executable, url, args)
    metadata: dict[str, Any] = {}
    if not args.dry_run:
        metadata = run_json_command(metadata_command)

    output_dir = output_dir_for(url, metadata or None, base_dir)
    command = build_download_command(executable, url, output_dir, args)

    plan = DownloadPlan(
        url=url,
        platform=platform,
        output_dir=str(output_dir),
        command=command,
        metadata_command=metadata_command,
        upload_enabled=should_upload(args),
    )

    if args.dry_run:
        return DownloadResult(
            url=url,
            platform=platform,
            output_dir=str(output_dir),
            files=[],
            metadata={},
            command=plan.command,
            dry_run=True,
            warnings=warnings,
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_text(output_dir / "source-url.txt", f"{url}\n")

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise DownloadError(f"yt-dlp failed with exit code {completed.returncode}")

    files = list_files(output_dir)
    result = DownloadResult(
        url=url,
        platform=platform,
        output_dir=str(output_dir),
        files=files,
        metadata=metadata_summary(metadata),
        command=command,
        warnings=warnings,
    )
    write_result(output_dir, result)

    if plan.upload_enabled:
        result.upload = upload_output(output_dir, output_dir.name)
        write_result(output_dir, result)

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-video-download",
        description="Download YouTube and X/Twitter video assets through yt-dlp.",
    )
    parser.add_argument("urls", nargs="+", help="YouTube, X.com, or Twitter URLs")
    parser.add_argument("--quality", choices=QUALITY_CHOICES, default="best", help="Quality cap or audio alias")
    parser.add_argument("--format", choices=VIDEO_FORMAT_CHOICES, default="mp4", help="Video container")
    parser.add_argument("--audio-only", action="store_true", help="Download audio only")
    parser.add_argument("--audio-format", choices=AUDIO_FORMAT_CHOICES, default="m4a", help="Audio output format")
    parser.add_argument("--thumbnail", action=argparse.BooleanOptionalAction, default=True, help="Download thumbnail")
    parser.add_argument("--thumbnail-only", action="store_true", help="Download metadata and thumbnail only")
    parser.add_argument("--metadata", action=argparse.BooleanOptionalAction, default=True, help="Write info JSON")
    parser.add_argument("--subtitles", action="store_true", help="Download subtitles and automatic subtitles")
    parser.add_argument("--languages", default="", help="Subtitle language list, e.g. zh,en,ja")
    parser.add_argument("--cookies-from-browser", help="Browser cookies source for yt-dlp, e.g. chrome, safari")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Base output directory")
    parser.add_argument("--upload", action="store_true", help="Upload task folders through guige-drive-upload")
    parser.add_argument("--no-upload", action="store_true", help="Disable upload even if GUIGE_DRIVE_UPLOAD=1")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without downloading")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    results: list[DownloadResult] = []
    errors: list[dict[str, str]] = []

    for url in args.urls:
        try:
            results.append(process_url(url, args))
        except Exception as error:
            errors.append({"url": url, "error": str(error)})

    if args.json_output:
        payload = {
            "success": not errors,
            "results": [asdict(result) for result in results],
            "errors": errors,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(result.output_dir)
            if result.upload:
                print(result.upload.get("drive_folder", "uploaded"))
        for error in errors:
            print(f"Error for {error['url']}: {error['error']}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
