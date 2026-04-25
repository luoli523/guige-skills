from __future__ import annotations

import base64
import os
import re
from pathlib import Path
from typing import Any

from ..files import guess_mime_type
from ..types import CliArgs, Quality
from .base import download_bytes, post_json, post_multipart


def parse_aspect_ratio(value: str | None) -> tuple[float, float] | None:
    if not value:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$", value)
    if not match:
        return None
    width = float(match.group(1))
    height = float(match.group(2))
    if width <= 0 or height <= 0:
        return None
    return width, height


def _is_gpt_image(model: str) -> bool:
    return "gpt-image" in model


def _is_gpt_image_2(model: str) -> bool:
    return "gpt-image-2" in model


def _round_to_multiple(value: float, multiple: int) -> int:
    return max(multiple, round(value / multiple) * multiple)


def _gpt_image_2_size_from_ar(aspect_ratio: str | None, quality: Quality | None) -> str:
    parsed = parse_aspect_ratio(aspect_ratio)
    ratio = (parsed[0] / parsed[1]) if parsed else 1
    if not parsed or abs(ratio - 1) < 0.1:
        edge = 2048 if quality == "2k" else 1024
        return f"{edge}x{edge}"

    target_long_edge = 2048 if quality == "2k" else 1024
    if ratio > 1:
        width = target_long_edge
        height = _round_to_multiple(width / ratio, 16)
    else:
        height = target_long_edge
        width = _round_to_multiple(height * ratio, 16)

    while width * height < 655_360:
        if ratio > 1:
            width += 16
            height = _round_to_multiple(width / ratio, 16)
        else:
            height += 16
            width = _round_to_multiple(height * ratio, 16)

    return f"{width}x{height}"


def get_openai_size(model: str, aspect_ratio: str | None, quality: Quality | None) -> str:
    if "dall-e-2" in model:
        return "1024x1024"
    if _is_gpt_image_2(model):
        return _gpt_image_2_size_from_ar(aspect_ratio, quality)

    if "dall-e-3" in model:
        sizes = {
            "square": "1024x1024",
            "landscape": "1792x1024",
            "portrait": "1024x1792",
        }
    else:
        sizes = {
            "square": "1024x1024",
            "landscape": "1536x1024",
            "portrait": "1024x1536",
        }

    parsed = parse_aspect_ratio(aspect_ratio)
    if not parsed:
        return sizes["square"]
    ratio = parsed[0] / parsed[1]
    if abs(ratio - 1) < 0.1:
        return sizes["square"]
    if ratio > 1.5:
        return sizes["landscape"]
    if ratio < 0.67:
        return sizes["portrait"]
    return sizes["square"]


def get_openai_quality(model: str, quality: Quality | None) -> str | None:
    if "dall-e-3" in model:
        return "hd" if quality == "2k" else "standard"
    if _is_gpt_image(model):
        return "high" if quality == "2k" else "medium"
    return None


def _parse_pixel_size(value: str) -> tuple[int, int] | None:
    match = re.match(r"^(\d+)\s*[xX]\s*(\d+)$", value)
    if not match:
        return None
    width = int(match.group(1))
    height = int(match.group(2))
    if width <= 0 or height <= 0:
        return None
    return width, height


def validate_args(model: str, args: CliArgs) -> None:
    if args.n < 1 or args.n > 10:
        raise ValueError("--n must be between 1 and 10")
    if "dall-e-3" in model and args.n != 1:
        raise ValueError("dall-e-3 only supports --n 1")
    if args.reference_images and ("dall-e-2" in model or "dall-e-3" in model):
        raise ValueError("OpenAI reference images require a GPT Image model.")

    if not _is_gpt_image_2(model):
        return

    if args.aspect_ratio and not args.size:
        parsed = parse_aspect_ratio(args.aspect_ratio)
        if not parsed:
            raise ValueError(f"Invalid gpt-image-2 aspect ratio: {args.aspect_ratio}")
        ratio = parsed[0] / parsed[1]
        if max(ratio, 1 / ratio) > 3:
            raise ValueError("gpt-image-2 aspect ratio must not exceed 3:1.")

    if not args.size:
        return

    parsed_size = _parse_pixel_size(args.size)
    if not parsed_size:
        raise ValueError(f"Invalid gpt-image-2 --size: {args.size}. Expected <width>x<height>.")
    width, height = parsed_size
    total_pixels = width * height
    ratio = max(width, height) / min(width, height)
    if max(width, height) > 3840:
        raise ValueError("gpt-image-2 --size maximum edge length must be 3840px or less.")
    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("gpt-image-2 --size width and height must both be multiples of 16px.")
    if ratio > 3:
        raise ValueError("gpt-image-2 --size long edge to short edge ratio must not exceed 3:1.")
    if total_pixels < 655_360 or total_pixels > 8_294_400:
        raise ValueError("gpt-image-2 --size total pixels must be between 655,360 and 8,294,400.")


def build_generations_body(prompt: str, model: str, args: CliArgs) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": args.n,
        "size": args.size or get_openai_size(model, args.aspect_ratio, args.quality),
    }
    quality = get_openai_quality(model, args.quality)
    if quality:
        body["quality"] = quality
    if not _is_gpt_image(model):
        body["response_format"] = "b64_json"
    return body


def extract_image_from_response(result: dict[str, Any]) -> bytes:
    data = result.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("No image in OpenAI response")

    first = data[0]
    if not isinstance(first, dict):
        raise RuntimeError("Unexpected OpenAI image response")

    b64_json = first.get("b64_json")
    if isinstance(b64_json, str) and b64_json:
        return base64.b64decode(b64_json)

    url = first.get("url")
    if isinstance(url, str) and url:
        return download_bytes(url)

    raise RuntimeError("No image data in OpenAI response")


def generate_image(prompt: str, model: str, args: CliArgs) -> bytes:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Guige-scoped OPENAI_API_KEY is required")

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}"}
    validate_args(model, args)

    if args.reference_images:
        return _generate_edit(base_url, headers, prompt, model, args)

    result = post_json(f"{base_url}/images/generations", headers, build_generations_body(prompt, model, args))
    return extract_image_from_response(result)


def _generate_edit(base_url: str, headers: dict[str, str], prompt: str, model: str, args: CliArgs) -> bytes:
    fields = {
        "model": model,
        "prompt": prompt,
        "size": args.size or get_openai_size(model, args.aspect_ratio, args.quality),
    }
    quality = get_openai_quality(model, args.quality)
    if quality and quality not in {"standard", "hd"}:
        fields["quality"] = quality

    files = []
    for ref_path in args.reference_images:
        path = Path(ref_path).expanduser().resolve()
        files.append(("image[]", path.name, guess_mime_type(str(path)), path.read_bytes()))

    result = post_multipart(f"{base_url}/images/edits", headers, fields, files)
    return extract_image_from_response(result)
