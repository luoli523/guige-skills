from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Provider = Literal["openai", "google"]
Quality = Literal["normal", "2k"]
ImageSize = Literal["1K", "2K", "4K"]


@dataclass
class CliArgs:
    prompt: str | None = None
    prompt_files: list[str] = field(default_factory=list)
    image_path: str | None = None
    provider: Provider | None = None
    model: str | None = None
    aspect_ratio: str | None = None
    size: str | None = None
    quality: Quality | None = None
    image_size: ImageSize | None = None
    reference_images: list[str] = field(default_factory=list)
    n: int = 1
    json_output: bool = False


@dataclass
class ExtendConfig:
    version: int = 1
    default_provider: Provider | None = None
    default_quality: Quality | None = None
    default_aspect_ratio: str | None = None
    default_image_size: ImageSize | None = None
    default_model: dict[Provider, str | None] = field(
        default_factory=lambda: {"openai": None, "google": None}
    )


@dataclass
class PreparedTask:
    prompt: str
    args: CliArgs
    provider: Provider
    model: str
    output_path: str


@dataclass
class TaskResult:
    provider: Provider
    model: str
    output_path: str
    success: bool
    error: str | None = None
