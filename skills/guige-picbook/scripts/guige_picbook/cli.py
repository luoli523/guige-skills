"""Command line interface for guige-picbook."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .core.generator import PictureBookGenerator
from .core.models import BookConfig, Language
from .utils.config import get_settings

app = typer.Typer(
    name="guige-picbook",
    help="""Generate children's picture books from a topic.

Quick start:
  guige-picbook generate ocean --no-slides
  guige-picbook generate 恐龙 --lang zh --slides
  guige-picbook generate space --chapters 8 --min-age 8 --max-age 12
""",
)
console = Console()


@dataclass
class GeneratedArtifacts:
    book_path: Path | None = None
    slides_path: Path | None = None
    upload_folder: str | None = None


def slugify(value: str, fallback: str = "picbook", max_length: int = 80) -> str:
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


def _default_output_path(topic: str, output_dir: str) -> Path:
    slug = slugify(topic)
    return Path(output_dir).expanduser() / slug / f"{slug}.md"


@app.command()
def generate(
    topic: str = typer.Argument(..., help="Picture book topic, e.g. dinosaur, ocean, 恐龙"),
    language: str = typer.Option(
        "en",
        "--lang",
        "-l",
        help="Output language: en, zh, ja, ko",
    ),
    chapters: int = typer.Option(
        5,
        "--chapters",
        "-c",
        help="Chapter count, 3-10",
        min=3,
        max=10,
    ),
    min_age: int = typer.Option(7, "--min-age", help="Minimum target age"),
    max_age: int = typer.Option(10, "--max-age", help="Maximum target age"),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Markdown output file. Defaults to <output-dir>/<topic-slug>/<topic-slug>.md",
    ),
    output_dir: str | None = typer.Option(
        None,
        "--output-dir",
        help="Root output directory when --output is not set. Defaults to Settings.output_dir.",
    ),
    slides: bool = typer.Option(
        True,
        "--slides/--no-slides",
        "--nlm-slides/--no-nlm-slides",
        help="Generate NotebookLM Slides PDF. Enabled by default.",
    ),
    nlm_instructions: str | None = typer.Option(
        None,
        "--nlm-instructions",
        help="NotebookLM custom instructions.",
    ),
    nlm_format: str | None = typer.Option(
        None,
        "--nlm-format",
        help="Slides format: detailed or presenter.",
    ),
    nlm_length: str | None = typer.Option(
        None,
        "--nlm-length",
        help="Slides length: default or short.",
    ),
    telegram: bool = typer.Option(
        False,
        "--telegram",
        "--tg",
        help="Send the Slides PDF to Telegram.",
    ),
    upload: bool = typer.Option(
        False,
        "--upload/--no-upload",
        help="Upload generated materials with guige-drive-upload.",
    ),
):
    """Generate a children's picture book, optionally with NotebookLM Slides."""
    try:
        lang = Language(language)
    except ValueError:
        console.print(f"[red]Unsupported language: {language}[/red]")
        console.print("Supported languages: zh, en, ja, ko")
        raise typer.Exit(1)

    if min_age > max_age:
        console.print("[red]--min-age cannot be greater than --max-age[/red]")
        raise typer.Exit(1)

    settings = get_settings()
    output_path = (
        Path(output).expanduser()
        if output
        else _default_output_path(topic, output_dir or settings.output_dir)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = BookConfig(
        topic=topic,
        language=lang,
        age_range=(min_age, max_age),
        chapter_count=chapters,
    )

    console.print(
        Panel(
            f"[bold]Topic:[/bold] {topic}\n"
            f"[bold]Language:[/bold] {lang.value}\n"
            f"[bold]Target age:[/bold] {min_age}-{max_age}\n"
            f"[bold]Chapters:[/bold] {chapters}\n"
            f"[bold]Output:[/bold] {output_path}",
            title="guige-picbook",
            border_style="blue",
        )
    )

    try:
        artifacts = asyncio.run(
            _generate_async(
                config=config,
                settings=settings,
                output_path=output_path,
                lang=lang,
                slides=slides,
                nlm_instructions=nlm_instructions,
                nlm_format=nlm_format,
                nlm_length=nlm_length,
                telegram=telegram,
            )
        )
    except typer.Exit:
        raise
    except Exception as error:
        console.print(f"[red]Generation failed: {error}[/red]")
        raise typer.Exit(1)

    artifacts.upload_folder = _maybe_upload(artifacts, topic, upload)
    _print_summary(artifacts)


async def _generate_async(
    config: BookConfig,
    settings,
    output_path: Path,
    lang: Language,
    slides: bool,
    nlm_instructions: str | None,
    nlm_format: str | None,
    nlm_length: str | None,
    telegram: bool,
) -> GeneratedArtifacts:
    artifacts = GeneratedArtifacts(book_path=output_path)

    if slides:
        from .services.notebooklm import NotebookLMService

        if output_path.exists():
            console.print(f"[cyan]Using existing book: {output_path}[/cyan]")
            markdown_content = output_path.read_text(encoding="utf-8")
        else:
            console.print("[cyan]Book not found, generating Markdown first...[/cyan]")
            book = await PictureBookGenerator(settings).generate(config)
            markdown_content = book.to_markdown()
            output_path.write_text(markdown_content, encoding="utf-8")
            console.print(f"[green]Book saved: {output_path}[/green]")

        console.print("\n[cyan]Generating NotebookLM Slides...[/cyan]")
        try:
            notebooklm_service = NotebookLMService(settings)
        except ImportError as error:
            raise RuntimeError(
                "NotebookLM dependency is required by default. "
                "Run `python3.11 skills/guige-picbook/scripts/main.py setup`."
            ) from error

        slides_language = "zh" if lang == Language.CHINESE else lang.value
        try:
            slides_path = await notebooklm_service.upload_and_generate_slides(
                markdown_content,
                title=output_path.name,
                download_dir=str(output_path.parent),
                instructions=nlm_instructions,
                language=slides_language,
                slide_format=nlm_format,
                slide_length=nlm_length,
            )
        except Exception as error:
            raise RuntimeError(
                "NotebookLM Slides generation failed. Markdown was kept at "
                f"{output_path}. Check NotebookLM login/network and retry."
            ) from error

        artifacts.slides_path = Path(slides_path)
        console.print(f"[green]Slides saved: {slides_path}[/green]")
    else:
        book = await PictureBookGenerator(settings).generate(config)
        markdown_content = book.to_markdown()
        output_path.write_text(markdown_content, encoding="utf-8")
        console.print(f"[green]Book saved: {output_path}[/green]")

    if artifacts.slides_path and telegram:
        await _send_pdf_to_telegram_async(settings, str(artifacts.slides_path))

    return artifacts


async def _send_pdf_to_telegram_async(settings, pdf_path: str) -> None:
    """Send a PDF file to Telegram."""
    from .services.telegram import TelegramService

    try:
        tg_service = TelegramService(settings)
    except ValueError as error:
        console.print(f"[yellow]{error}[/yellow]")
        return

    console.print("\n[cyan]Sending PDF to Telegram...[/cyan]")
    try:
        await tg_service.send_document(pdf_path)
        console.print("[green]Sent to Telegram.[/green]")
    except Exception as error:
        console.print(f"[yellow]Telegram send failed: {error}[/yellow]")


def _maybe_upload(artifacts: GeneratedArtifacts, topic: str, upload: bool) -> str | None:
    should_upload = upload or os.environ.get("GUIGE_DRIVE_UPLOAD") == "1"
    if not should_upload:
        return None

    paths: list[str] = []
    if artifacts.book_path:
        paths.append(str(artifacts.book_path.parent))
    elif artifacts.slides_path:
        paths.append(str(artifacts.slides_path.parent))

    if not paths:
        return None

    skill_dir = Path(__file__).resolve().parents[2]
    drive_script = skill_dir.parent / "guige-drive-upload" / "scripts" / "main.py"
    if not drive_script.exists():
        console.print("[yellow]guige-drive-upload script not found; upload skipped.[/yellow]")
        return None

    command = [
        sys.executable,
        str(drive_script),
        "--skill",
        "guige-picbook",
        "--task",
        topic,
        "--paths",
        *paths,
        "--json",
    ]

    console.print("[cyan]Uploading generated materials to Google Drive...[/cyan]")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        console.print("[yellow]Upload failed; local files are kept.[/yellow]")
        if result.stderr.strip():
            console.print(f"[dim]{result.stderr.strip()}[/dim]")
        elif result.stdout.strip():
            console.print(f"[dim]{result.stdout.strip()}[/dim]")
        return None

    try:
        payload = json.loads(result.stdout)
        folder = payload.get("drive_folder")
    except json.JSONDecodeError:
        folder = result.stdout.strip()
    if folder:
        console.print(f"[green]Uploaded to: {folder}[/green]")
    return folder or None


def _print_summary(artifacts: GeneratedArtifacts) -> None:
    console.print("\n[bold]Done[/bold]")
    if artifacts.book_path:
        console.print(f"Book: {artifacts.book_path}")
    if artifacts.slides_path:
        console.print(f"Slides: {artifacts.slides_path}")
    if artifacts.upload_folder:
        console.print(f"Drive: {artifacts.upload_folder}")


@app.command()
def languages():
    """List supported output languages."""
    names = {
        "zh": "Chinese",
        "en": "English",
        "ja": "Japanese",
        "ko": "Korean",
    }
    for lang in Language:
        console.print(f"{lang.value}: {names.get(lang.value, lang.value)}")


@app.command()
def version():
    """Show version."""
    from . import __version__

    console.print(f"guige-picbook v{__version__}")


@app.command("notebooklm-login")
def notebooklm_login():
    """Print NotebookLM login instructions."""
    from .services.notebooklm import NotebookLMService

    service = NotebookLMService(get_settings())
    try:
        asyncio.run(service.login())
    except ImportError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    except Exception as error:
        console.print(f"[red]Operation failed: {error}[/red]")
        raise typer.Exit(1)


@app.command("upload-to-notebooklm")
def upload_to_notebooklm(
    file_path: str = typer.Argument(..., help="Markdown file to upload."),
):
    """Upload an existing picture book Markdown file to NotebookLM."""
    from .services.notebooklm import NotebookLMService

    path = Path(file_path).expanduser()
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)

    service = NotebookLMService(get_settings())
    try:
        console.print("Uploading to NotebookLM...")
        notebook_id, source_id, source_title = asyncio.run(
            service.upload(path.read_text(encoding="utf-8"), title=path.name)
        )
        console.print("[green]Upload succeeded.[/green]")
        console.print(f"Notebook: {service.notebook_name} ({notebook_id})")
        console.print(f"Source: {source_title} ({source_id})")
        console.print(f"https://notebooklm.google.com/notebook/{notebook_id}")
    except ImportError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    except Exception as error:
        console.print(f"[red]Upload failed: {error}[/red]")
        raise typer.Exit(1)


@app.command("generate-slides")
def generate_slides(
    notebook_url: str = typer.Argument(..., help="NotebookLM notebook URL or ID."),
    output_dir: str | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Slides download directory. Defaults to the current directory.",
    ),
):
    """Generate and download Slides from an existing NotebookLM notebook."""
    from .services.notebooklm import NotebookLMService

    service = NotebookLMService(get_settings())
    notebook_id = notebook_url
    if "notebooklm.google.com/notebook/" in notebook_url:
        notebook_id = notebook_url.split("/notebook/")[-1].split("?")[0]

    try:
        console.print("[cyan]Generating Slides...[/cyan]")
        slides_path = asyncio.run(
            service.generate_slides(notebook_id, download_dir=output_dir)
        )
        console.print(f"[green]Slides saved: {slides_path}[/green]")
    except ImportError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    except Exception as error:
        console.print(f"[red]Slides generation failed: {error}[/red]")
        raise typer.Exit(1)


@app.command()
def share(
    pdf_path: str = typer.Argument(..., help="Slides PDF file."),
    telegram: bool = typer.Option(False, "--telegram", "--tg", help="Send PDF to Telegram."),
):
    """Share an existing Slides PDF."""
    pdf = Path(pdf_path).expanduser()
    if not pdf.exists():
        console.print(f"[red]File not found: {pdf}[/red]")
        raise typer.Exit(1)

    if telegram:
        asyncio.run(_send_pdf_to_telegram_async(get_settings(), str(pdf)))


if __name__ == "__main__":
    app()
