from __future__ import annotations

import argparse
import importlib
import json
import sys

from .config import detect_provider, get_model_for_provider, load_extend_config, merge_config
from .env import load_env_files
from .files import (
    normalize_output_image_path,
    read_prompt_from_files,
    read_prompt_from_stdin,
    resolve_download_output_path,
    validate_reference_images,
    write_image,
)
from .types import CliArgs, PreparedTask, Provider, TaskResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guige-imagen",
        description="Generate images with OpenAI or Google from a Python-native Gui Ge skill.",
    )
    parser.add_argument("-p", "--prompt", help="Prompt text")
    parser.add_argument("--promptfiles", nargs="+", default=[], help="Prompt files to concatenate")
    parser.add_argument(
        "--image",
        dest="image_path",
        help="Optional output filename/extension hint; final images are saved under ~/Downloads/guige-skill-imagen",
    )
    parser.add_argument("--provider", choices=["openai", "google"], help="Image provider")
    parser.add_argument("-m", "--model", help="Provider model ID")
    parser.add_argument("--ar", dest="aspect_ratio", help="Aspect ratio, e.g. 16:9 or 1:1")
    parser.add_argument("--size", help="Provider-specific size, e.g. 1024x1024")
    parser.add_argument("--quality", choices=["normal", "2k"], help="Quality preset")
    parser.add_argument("--imageSize", choices=["1K", "2K", "4K"], help="Google image size")
    parser.add_argument("--ref", nargs="+", default=[], dest="reference_images", help="Reference images")
    parser.add_argument("--n", type=int, default=1, help="Number of images requested from provider")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def parse_args(argv: list[str]) -> CliArgs:
    namespace = build_parser().parse_args(argv)
    provider: Provider | None = namespace.provider
    return CliArgs(
        prompt=namespace.prompt,
        prompt_files=namespace.promptfiles,
        image_path=namespace.image_path,
        provider=provider,
        model=namespace.model,
        aspect_ratio=namespace.aspect_ratio,
        size=namespace.size,
        quality=namespace.quality,
        image_size=namespace.imageSize,
        reference_images=namespace.reference_images,
        n=namespace.n,
        json_output=namespace.json_output,
    )


def _load_prompt(args: CliArgs) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_files:
        return read_prompt_from_files(args.prompt_files)
    stdin_prompt = read_prompt_from_stdin()
    if stdin_prompt:
        return stdin_prompt
    raise ValueError("Prompt is required. Use --prompt, --promptfiles, or stdin.")


def _load_provider_module(provider: Provider):
    return importlib.import_module(f"guige_imagen.providers.{provider}")


def prepare_task(args: CliArgs) -> PreparedTask:
    load_env_files()
    config = load_extend_config()
    merged_args = merge_config(args, config)
    if not merged_args.quality:
        merged_args.quality = "2k"

    prompt = _load_prompt(merged_args)
    if merged_args.reference_images:
        validate_reference_images(merged_args.reference_images)

    provider = detect_provider(merged_args)
    model = get_model_for_provider(provider, merged_args.model, config)
    output_path = resolve_download_output_path(prompt, merged_args.image_path)
    return PreparedTask(
        prompt=prompt,
        args=merged_args,
        provider=provider,
        model=model,
        output_path=str(output_path),
    )


def run(argv: list[str]) -> TaskResult:
    task = prepare_task(parse_args(argv))
    provider_module = _load_provider_module(task.provider)
    print(f"Using {task.provider} / {task.model}", file=sys.stderr)
    image_data = provider_module.generate_image(task.prompt, task.model, task.args)
    write_image(normalize_output_image_path(task.output_path), image_data)
    return TaskResult(
        provider=task.provider,
        model=task.model,
        output_path=task.output_path,
        success=True,
    )


def main(argv: list[str] | None = None) -> int:
    resolved_argv = sys.argv[1:] if argv is None else argv
    json_requested = "--json" in resolved_argv
    try:
        result = run(resolved_argv)
        if result.success:
            if json_requested:
                print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
            else:
                print(f"Image saved: {result.output_path}", file=sys.stderr)
            return 0
    except Exception as error:
        if json_requested:
            print(
                json.dumps(
                    {"success": False, "error": str(error)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Error: {error}", file=sys.stderr)
        return 1

    return 1
