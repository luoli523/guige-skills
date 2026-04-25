from __future__ import annotations

import os
import re
from pathlib import Path

from .types import CliArgs, ExtendConfig, ImageSize, Provider, Quality

PROVIDERS = {"openai", "google"}
QUALITIES = {"normal", "2k"}
IMAGE_SIZES = {"1K", "2K", "4K"}


def extract_yaml_frontmatter(content: str) -> str | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", content, re.DOTALL)
    return match.group(1) if match else None


def _clean_scalar(value: str) -> str | None:
    stripped = value.strip()
    if stripped in {"", "null", "~"}:
        return None
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith("'") and stripped.endswith("'")
    ):
        return stripped[1:-1]
    return stripped


def parse_simple_yaml(yaml: str) -> ExtendConfig:
    config = ExtendConfig()
    current_section: str | None = None

    for raw_line in yaml.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, value = raw_line.strip().split(":", 1)
        cleaned = _clean_scalar(value)

        if indent == 0:
            current_section = key if cleaned is None else None
            if key == "version":
                config.version = int(cleaned or "1")
            elif key == "default_provider":
                if cleaned is not None and cleaned not in PROVIDERS:
                    raise ValueError(f"Invalid default_provider: {cleaned}")
                config.default_provider = cleaned  # type: ignore[assignment]
            elif key == "default_quality":
                if cleaned is not None and cleaned not in QUALITIES:
                    raise ValueError(f"Invalid default_quality: {cleaned}")
                config.default_quality = cleaned  # type: ignore[assignment]
            elif key == "default_aspect_ratio":
                config.default_aspect_ratio = cleaned
            elif key == "default_image_size":
                if cleaned is not None and cleaned not in IMAGE_SIZES:
                    raise ValueError(f"Invalid default_image_size: {cleaned}")
                config.default_image_size = cleaned  # type: ignore[assignment]
            elif key == "default_model":
                current_section = "default_model"
            continue

        if current_section == "default_model" and indent >= 2 and key in PROVIDERS:
            config.default_model[key] = cleaned  # type: ignore[index]

    return config


def get_extend_config_paths(cwd: Path | None = None, home: Path | None = None) -> list[Path]:
    resolved_cwd = cwd or Path.cwd()
    resolved_home = home or Path.home()
    xdg_config_home = Path(os.environ.get("XDG_CONFIG_HOME", resolved_home / ".config"))
    return [
        resolved_cwd / ".guige-skills" / "guige-imagen" / "EXTEND.md",
        xdg_config_home / "guige-skills" / "guige-imagen" / "EXTEND.md",
        resolved_home / ".guige-skills" / "guige-imagen" / "EXTEND.md",
    ]


def load_extend_config(cwd: Path | None = None, home: Path | None = None) -> ExtendConfig:
    for path in get_extend_config_paths(cwd, home):
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        yaml = extract_yaml_frontmatter(content)
        if yaml is None:
            continue
        return parse_simple_yaml(yaml)
    return ExtendConfig()


def merge_config(args: CliArgs, config: ExtendConfig) -> CliArgs:
    args.provider = args.provider or config.default_provider
    args.quality = args.quality or config.default_quality
    args.aspect_ratio = args.aspect_ratio or config.default_aspect_ratio
    args.image_size = args.image_size or config.default_image_size
    return args


def detect_provider(args: CliArgs) -> Provider:
    if args.provider:
        return args.provider

    model = (args.model or "").lower()
    if "gpt-image" in model or "dall-e" in model:
        return "openai"
    if "gemini" in model or "imagen" in model:
        return "google"

    has_google = bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if args.reference_images:
        if has_google:
            return "google"
        if has_openai:
            return "openai"
        raise ValueError(
            "Reference images require a guige-scoped GOOGLE_API_KEY/GEMINI_API_KEY or OPENAI_API_KEY, "
            "or pass --provider explicitly."
        )

    if has_google:
        return "google"
    if has_openai:
        return "openai"

    raise ValueError(
        "No guige-scoped API key found. Add GOOGLE_API_KEY/GEMINI_API_KEY or OPENAI_API_KEY "
        "to <cwd>/.guige-skills/.env or ~/.guige-skills/.env. To deliberately use shell "
        "provider env, set GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1."
    )


def get_model_for_provider(provider: Provider, requested_model: str | None, config: ExtendConfig) -> str:
    if requested_model:
        return requested_model
    configured = config.default_model.get(provider)
    if configured:
        return configured
    if provider == "openai":
        return os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-1.5"
    return os.environ.get("GOOGLE_IMAGE_MODEL") or "gemini-3-pro-image-preview"
