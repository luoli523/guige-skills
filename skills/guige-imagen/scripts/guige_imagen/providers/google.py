from __future__ import annotations

import base64
import os
from typing import Any

from ..files import read_image_as_base64
from ..types import CliArgs, ImageSize
from .base import post_json


def normalize_model_id(model: str) -> str:
    return model.removeprefix("models/")


def is_imagen_model(model: str) -> bool:
    return "imagen" in normalize_model_id(model).lower()


def get_google_image_size(args: CliArgs) -> ImageSize:
    if args.image_size:
        return args.image_size
    return "2K" if args.quality == "2k" else "1K"


def get_google_base_url() -> str:
    return os.environ.get("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")


def build_google_url(pathname: str) -> str:
    base_url = get_google_base_url()
    cleaned = pathname.lstrip("/")
    if base_url.endswith("/v1beta"):
        return f"{base_url}/{cleaned}"
    return f"{base_url}/v1beta/{cleaned}"


def _model_path(model: str) -> str:
    return f"models/{normalize_model_id(model)}"


def _api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Guige-scoped GOOGLE_API_KEY or GEMINI_API_KEY is required")
    return key


def add_aspect_to_prompt(prompt: str, aspect_ratio: str | None, quality: str | None = None) -> str:
    result = prompt
    if aspect_ratio:
        result += f" Aspect ratio: {aspect_ratio}."
    if quality == "2k":
        result += " High resolution 2048px."
    return result


def extract_inline_image_data(response: dict[str, Any]) -> str | None:
    for candidate in response.get("candidates", []) or []:
        content = candidate.get("content") if isinstance(candidate, dict) else None
        parts = content.get("parts", []) if isinstance(content, dict) else []
        for part in parts:
            if not isinstance(part, dict):
                continue
            inline = part.get("inlineData") or part.get("inline_data")
            if isinstance(inline, dict):
                data = inline.get("data")
                if isinstance(data, str) and data:
                    return data
    return None


def extract_predicted_image_data(response: dict[str, Any]) -> str | None:
    candidates = []
    candidates.extend(response.get("predictions", []) or [])
    candidates.extend(response.get("generatedImages", []) or [])
    candidates.extend(response.get("generated_images", []) or [])

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        for key in ("imageBytes", "bytesBase64Encoded", "data"):
            value = candidate.get(key)
            if isinstance(value, str) and value:
                return value
        image = candidate.get("image")
        if isinstance(image, dict):
            for key in ("imageBytes", "bytesBase64Encoded", "data"):
                value = image.get(key)
                if isinstance(value, str) and value:
                    return value
    return None


def generate_image(prompt: str, model: str, args: CliArgs) -> bytes:
    if args.n < 1 or args.n > 4:
        raise ValueError("Google provider supports --n from 1 to 4")
    if is_imagen_model(model):
        return _generate_with_imagen(prompt, model, args)
    return _generate_with_gemini(prompt, model, args)


def _generate_with_gemini(prompt: str, model: str, args: CliArgs) -> bytes:
    parts: list[dict[str, Any]] = []
    for ref_path in args.reference_images:
        data, mime_type = read_image_as_base64(ref_path)
        parts.append({"inline_data": {"mime_type": mime_type, "data": data}})
    parts.append({"text": add_aspect_to_prompt(prompt, args.aspect_ratio)})

    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"imageSize": get_google_image_size(args)},
        },
    }
    result = post_json(
        build_google_url(f"{_model_path(model)}:generateContent"),
        {"x-goog-api-key": _api_key()},
        body,
    )
    image_data = extract_inline_image_data(result)
    if not image_data:
        raise RuntimeError("No image in Google Gemini response")
    return base64.b64decode(image_data)


def _generate_with_imagen(prompt: str, model: str, args: CliArgs) -> bytes:
    if args.reference_images:
        raise ValueError("Reference images are not supported with Google Imagen models.")

    image_size = get_google_image_size(args)
    if image_size == "4K":
        image_size = "2K"

    parameters: dict[str, Any] = {
        "sampleCount": args.n,
        "imageSize": image_size,
    }
    if args.aspect_ratio:
        parameters["aspectRatio"] = args.aspect_ratio

    body = {
        "instances": [{"prompt": add_aspect_to_prompt(prompt, args.aspect_ratio, args.quality)}],
        "parameters": parameters,
    }
    result = post_json(
        build_google_url(f"{_model_path(model)}:predict"),
        {"x-goog-api-key": _api_key()},
        body,
    )
    image_data = extract_predicted_image_data(result)
    if not image_data:
        raise RuntimeError("No image in Google Imagen response")
    return base64.b64decode(image_data)
