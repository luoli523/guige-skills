#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "beautifulsoup4",
#   "img2pdf",
#   "lxml",
#   "pillow",
#   "requests",
# ]
# ///
#
# Usage:
#   uv run scripts/download_to_drive.py <comic-detail-url> --target gdrive:HH/ --workers 20
#   uv run scripts/download_to_drive.py --list scripts/list.txt --target gdrive:HH/ --workers 20
#
# Notes:
#   - The script creates one PDF per chapter, uploads PDFs only, then deletes that comic's local cache.
#   - Use --no-upload to keep generated PDFs locally without uploading or deleting the cache.
#   - If uv cannot write its default cache in a sandbox, prefix with:
#     UV_CACHE_DIR=/private/tmp/uv-cache uv run scripts/download_to_drive.py ...
#
# Optional environment variables:
#   COMIC_UPLOAD_TARGET        Default value for --target.
#   COMIC_USER_AGENT           Override the request User-Agent.
#   COMIC_TITLE_SELECTOR       CSS selector for the comic title.
#   COMIC_CHAPTER_LINK_SELECTOR CSS selector for chapter links.
#   COMIC_IMAGE_SELECTOR       CSS selector for chapter images.
#   COMIC_IMAGE_HOST_ALIASES   Optional host fallback map, e.g. source.host=a.host,b.host;other.host=c.host
from __future__ import annotations

import argparse
import concurrent.futures
import html
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import img2pdf
import requests
from bs4 import BeautifulSoup
from PIL import Image


USER_AGENT = os.environ.get("COMIC_USER_AGENT", "Mozilla/5.0")
TITLE_SELECTOR = os.environ.get("COMIC_TITLE_SELECTOR", ".Introduct_Sub h1,h1")
CHAPTER_LINK_SELECTOR = os.environ.get("COMIC_CHAPTER_LINK_SELECTOR", "#mh-chapter-list-ol-0 a[href]")
IMAGE_SELECTOR = os.environ.get("COMIC_IMAGE_SELECTOR", "#currentCache img")
DEFAULT_UPLOAD_TARGET = os.environ.get("COMIC_UPLOAD_TARGET")


@dataclass(frozen=True)
class Chapter:
    index: int
    title: str
    url: str


def sanitize_filename(value: str, fallback: str = "untitled", max_length: int = 120) -> str:
    value = html.unescape(value).strip()
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    if not value:
        value = fallback
    return value[:max_length].rstrip(" .") or fallback


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )
    return s


def fetch_text(s: requests.Session, url: str) -> str:
    for attempt in range(1, 5):
        try:
            response = s.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.encoding or "utf-8"
            return response.text
        except Exception:
            if attempt == 4:
                raise
            time.sleep(1.5 * attempt)
    raise RuntimeError("unreachable")


def parse_comic_page(s: requests.Session, url: str) -> tuple[str, list[Chapter]]:
    soup = BeautifulSoup(fetch_text(s, url), "lxml")
    title_node = soup.select_one(TITLE_SELECTOR)
    comic_name = title_node.get_text(strip=True).strip("《》") if title_node else "comic"
    comic_name = sanitize_filename(comic_name, "comic")

    links = soup.select(CHAPTER_LINK_SELECTOR)
    chapters: list[Chapter] = []
    for link in links:
        text = link.get_text(" ", strip=True)
        href = link.get("href")
        if not href or not text:
            continue
        chapters.append(Chapter(index=0, title=sanitize_filename(text), url=urljoin(url, href)))

    # The page lists newest first. Reverse so files are numbered from chapter 1 onward.
    chapters = list(reversed(chapters))
    return comic_name, [Chapter(i, chapter.title, chapter.url) for i, chapter in enumerate(chapters, 1)]


def normalize_comic_url(url: str) -> str:
    parsed = urlparse(url)
    match = re.fullmatch(r"(/comic/[^/]+)/chapter-[^/]+\.html", parsed.path)
    if not match:
        return url
    return urlunparse(parsed._replace(path=f"{match.group(1)}.html", params="", query="", fragment=""))


def parse_image_urls(s: requests.Session, chapter_url: str) -> list[str]:
    soup = BeautifulSoup(fetch_text(s, chapter_url), "lxml")
    image_urls: list[str] = []
    for image in soup.select(IMAGE_SELECTOR):
        raw = image.get("data-original") or image.get("src")
        if not raw:
            continue
        full_url = urljoin(chapter_url, raw)
        if full_url not in image_urls:
            image_urls.append(full_url)
    return image_urls


def extension_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return ".jpg"


def image_url_candidates(url: str) -> list[str]:
    parsed = urlparse(url)
    candidates = [url]
    for host in configured_host_aliases(parsed.netloc):
        candidates.append(urlunparse(parsed._replace(netloc=host)))
    return candidates


def configured_host_aliases(source_host: str) -> list[str]:
    raw = os.environ.get("COMIC_IMAGE_HOST_ALIASES", "")
    aliases: list[str] = []
    for group in raw.split(";"):
        group = group.strip()
        if not group or "=" not in group:
            continue
        host, values = group.split("=", 1)
        if host.strip() != source_host:
            continue
        aliases.extend(value.strip() for value in values.split(",") if value.strip())
    return [host for host in aliases if host != source_host]


def download_file(
    s: requests.Session,
    url: str,
    destination: Path,
    referer: str,
) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    headers = {
        "Referer": referer,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "User-Agent": USER_AGENT,
    }
    tmp = destination.with_suffix(destination.suffix + ".part")
    last_error: Exception | None = None
    for candidate_url in image_url_candidates(url):
        for attempt in range(1, 6):
            try:
                with s.get(candidate_url, headers=headers, timeout=60, stream=True) as response:
                    response.raise_for_status()
                    with tmp.open("wb") as handle:
                        for chunk in response.iter_content(chunk_size=1024 * 256):
                            if chunk:
                                handle.write(chunk)
                if tmp.stat().st_size <= 0:
                    raise RuntimeError(f"empty download: {candidate_url}")
                tmp.replace(destination)
                return
            except Exception as error:
                last_error = error
                if tmp.exists():
                    tmp.unlink()
                if attempt == 5:
                    break
                time.sleep(1.5 * attempt)
    if last_error:
        raise last_error


def is_valid_pdf(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 1024


def filter_pdf_images(images: list[Path]) -> list[Path]:
    filtered: list[Path] = []
    for path in images:
        with Image.open(path) as image:
            width, height = image.size
        if width < 10 or height < 10:
            continue
        filtered.append(path)
    return filtered


def write_pdf(images: list[Path], output: Path) -> int:
    if is_valid_pdf(output):
        return -1
    if output.exists():
        output.unlink()
    images = filter_pdf_images(images)
    if not images:
        raise RuntimeError("No usable images to write PDF.")
    if output.exists() and output.stat().st_size > 0:
        return -1
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        handle.write(img2pdf.convert([str(path) for path in images]))
    return len(images)


def process_chapter(base_url: str, output_root: Path, chapter: Chapter) -> tuple[int, str, int, Path]:
    s = session()
    chapter_dir = output_root / "images" / f"{chapter.index:03d}_{chapter.title}"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_root / f"{chapter.index:03d}_{chapter.title}.pdf"
    if is_valid_pdf(pdf_path):
        return chapter.index, chapter.title, -1, pdf_path

    image_urls = parse_image_urls(s, chapter.url)
    if not image_urls:
        raise RuntimeError(f"No images found in {chapter.url}")

    image_paths: list[Path] = []
    for i, image_url in enumerate(image_urls, 1):
        image_path = chapter_dir / f"{i:03d}{extension_from_url(image_url)}"
        download_file(s, image_url, image_path, referer=chapter.url)
        image_paths.append(image_path)

    page_count = write_pdf(image_paths, pdf_path)
    return chapter.index, chapter.title, page_count, pdf_path


def upload_folder(local_folder: Path, target: str, comic_name: str) -> None:
    destination = target.rstrip("/")
    destination = destination if destination.endswith(":") else destination + "/"
    destination = f"{destination}{comic_name}"
    subprocess.run(
        ["rclone", "copy", str(local_folder), destination, "--filter", "+ *.pdf", "--filter", "- **"],
        check=True,
    )


def run_comic(url: str, output: str, target: str | None, workers: int, no_upload: bool) -> int:
    s = session()
    comic_url = normalize_comic_url(url)
    comic_name, chapters = parse_comic_page(s, comic_url)
    if not chapters:
        raise RuntimeError("No chapters found.")

    output_root = Path(output).expanduser().resolve() / comic_name
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Comic: {comic_name}")
    print(f"Chapters: {len(chapters)}")
    print(f"Output: {output_root}")
    sys.stdout.flush()

    failures: list[tuple[Chapter, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(process_chapter, comic_url, output_root, chapter): chapter
            for chapter in chapters
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            chapter = futures[future]
            try:
                index, title, image_count, pdf_path = future.result()
                completed += 1
                if image_count < 0:
                    print(f"[{completed}/{len(chapters)}] {index:03d} {title} -> cached, {pdf_path.name}")
                else:
                    print(f"[{completed}/{len(chapters)}] {index:03d} {title} -> {image_count} pages, {pdf_path.name}")
            except Exception as error:
                failures.append((chapter, str(error)))
                print(f"[FAIL] {chapter.index:03d} {chapter.title}: {error}", file=sys.stderr)
            sys.stdout.flush()

    if failures:
        print("Failures:", file=sys.stderr)
        for chapter, message in failures:
            print(f"- {chapter.index:03d} {chapter.title}: {message}", file=sys.stderr)
        return 1

    if not no_upload:
        if not target:
            raise RuntimeError("--target or COMIC_UPLOAD_TARGET is required unless --no-upload is set.")
        upload_folder(output_root, target, comic_name)
        print(f"Uploaded: {target.rstrip('/')}/{comic_name}")
        shutil.rmtree(output_root)
        print(f"Deleted local cache: {output_root}")

    return 0


def read_url_list(path: Path) -> list[str]:
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download chapters into PDFs and upload them.")
    parser.add_argument("url", nargs="?", help="Comic detail page URL.")
    parser.add_argument("--list", dest="list_file", help="File with one comic URL per line.")
    parser.add_argument("--output", default="/private/tmp/comic-downloads", help="Output base directory.")
    parser.add_argument("--target", default=DEFAULT_UPLOAD_TARGET, help="rclone target directory.")
    parser.add_argument("--workers", type=int, default=4, help="Number of chapters to process in parallel.")
    parser.add_argument("--no-upload", action="store_true", help="Skip remote upload.")
    args = parser.parse_args(argv)

    if bool(args.url) == bool(args.list_file):
        parser.error("Provide exactly one of URL or --list.")

    if args.list_file:
        urls = read_url_list(Path(args.list_file))
        if not urls:
            raise RuntimeError(f"No URLs found in {args.list_file}")
        failures: list[tuple[str, str]] = []
        for index, url in enumerate(urls, 1):
            print(f"\n=== [{index}/{len(urls)}] {url} ===")
            try:
                result = run_comic(url, args.output, args.target, args.workers, args.no_upload)
                if result:
                    failures.append((url, f"exit code {result}"))
            except Exception as error:
                failures.append((url, str(error)))
                print(f"[FAIL] {url}: {error}", file=sys.stderr)
            sys.stdout.flush()
        if failures:
            print("Batch failures:", file=sys.stderr)
            for url, message in failures:
                print(f"- {url}: {message}", file=sys.stderr)
            return 1
        return 0

    return run_comic(args.url, args.output, args.target, args.workers, args.no_upload)


if __name__ == "__main__":
    raise SystemExit(main())
