from __future__ import annotations

import base64
import mimetypes
import sys
from pathlib import Path

DEFAULT_IMAGE_OUTPUT_DIR = Path("~/Downloads/guige-skill-imagen").expanduser()
STOP_WORDS = {
    "a",
    "an",
    "and",
    "create",
    "draw",
    "for",
    "generate",
    "generation",
    "image",
    "in",
    "make",
    "of",
    "on",
    "photo",
    "picture",
    "render",
    "the",
    "this",
    "to",
    "with",
}


def read_prompt_from_files(files: list[str]) -> str:
    return "\n\n".join(Path(file).read_text(encoding="utf-8") for file in files)


def read_prompt_from_stdin() -> str | None:
    if sys.stdin.isatty():
        return None
    value = sys.stdin.read().strip()
    return value or None


def normalize_output_image_path(path: str, default_extension: str = ".png") -> Path:
    resolved = Path(path).expanduser().resolve()
    if resolved.suffix:
        return resolved
    return resolved.with_suffix(default_extension)


def extract_slug_source(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                return heading
    return content


def slugify_content(content: str, fallback: str = "image", max_length: int = 72) -> str:
    source = extract_slug_source(content).casefold()
    chars: list[str] = []
    previous_was_separator = False

    for char in source:
        if char.isalnum():
            chars.append(char)
            previous_was_separator = False
        elif not previous_was_separator:
            chars.append("-")
            previous_was_separator = True

    raw_slug = "".join(chars).strip("-")
    words = [word for word in raw_slug.split("-") if word and word not in STOP_WORDS]
    slug = "-".join(words) or fallback

    if len(slug) <= max_length:
        return slug

    truncated = slug[:max_length].rstrip("-")
    if "-" in truncated:
        truncated = truncated.rsplit("-", 1)[0]
    return truncated or fallback


def dedupe_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def resolve_download_output_path(
    prompt: str,
    requested_path: str | None = None,
    default_extension: str = ".png",
) -> Path:
    extension = default_extension
    if requested_path:
        requested_extension = Path(requested_path).suffix
        if requested_extension:
            extension = requested_extension

    filename = f"{slugify_content(prompt)}{extension}"
    return dedupe_path(DEFAULT_IMAGE_OUTPUT_DIR / filename)


def write_image(path: Path, image_data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_data)


def validate_reference_images(paths: list[str]) -> None:
    for value in paths:
        path = Path(value).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Reference image not found: {path}")
        if not path.is_file():
            raise ValueError(f"Reference image is not a file: {path}")


def guess_mime_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
    return guessed or "image/png"


def read_image_as_base64(path: str) -> tuple[str, str]:
    resolved = Path(path).expanduser().resolve()
    return base64.b64encode(resolved.read_bytes()).decode("ascii"), guess_mime_type(str(resolved))
