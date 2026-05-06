#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SlideImage:
    index: int
    filename: str
    path: Path


@dataclass
class PdfImage:
    width: int
    height: int
    color_space: str
    bits: int
    data: bytes
    filters: str


def find_slide_images(deck_dir: Path) -> list[SlideImage]:
    if not deck_dir.is_dir():
        raise FileNotFoundError(f"Deck directory not found: {deck_dir}")
    pattern = re.compile(r"^(\d+)-slide-.*\.(png|jpg|jpeg)$", re.IGNORECASE)
    slides: list[SlideImage] = []
    for path in deck_dir.iterdir():
        if not path.is_file():
            continue
        match = pattern.match(path.name)
        if match:
            slides.append(SlideImage(int(match.group(1)), path.name, path))
    slides.sort(key=lambda slide: (slide.index, slide.filename))
    if not slides:
        raise RuntimeError(f"No slide images found in {deck_dir}; expected NN-slide-*.png|jpg")
    return slides


def read_jpeg_size(data: bytes) -> tuple[int, int]:
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in {0xD8, 0xD9}:
            continue
        length = struct.unpack(">H", data[i : i + 2])[0]
        if 0xC0 <= marker <= 0xC3:
            height = struct.unpack(">H", data[i + 3 : i + 5])[0]
            width = struct.unpack(">H", data[i + 5 : i + 7])[0]
            return width, height
        i += length
    raise ValueError("Could not read JPEG dimensions")


def parse_png(data: bytes) -> tuple[int, int, int, int, bytes]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature")
    pos = 8
    width = height = bit_depth = color_type = None
    idat_parts: list[bytes] = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk_data)
            if interlace != 0:
                raise ValueError("Interlaced PNG is not supported")
            if bit_depth != 8:
                raise ValueError("Only 8-bit PNG is supported")
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break
    if width is None or height is None or bit_depth is None or color_type is None:
        raise ValueError("PNG missing IHDR")
    return width, height, bit_depth, color_type, zlib.decompress(b"".join(idat_parts))


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def unfilter_png(width: int, height: int, color_type: int, raw: bytes) -> bytes:
    channels_by_type = {0: 1, 2: 3, 4: 2, 6: 4}
    if color_type not in channels_by_type:
        raise ValueError(f"Unsupported PNG color type: {color_type}")
    channels = channels_by_type[color_type]
    stride = width * channels
    bpp = channels
    rows: list[bytes] = []
    prev = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        row = bytearray(raw[offset : offset + stride])
        offset += stride
        for i in range(stride):
            left = row[i - bpp] if i >= bpp else 0
            up = prev[i]
            up_left = prev[i - bpp] if i >= bpp else 0
            if filter_type == 1:
                row[i] = (row[i] + left) & 0xFF
            elif filter_type == 2:
                row[i] = (row[i] + up) & 0xFF
            elif filter_type == 3:
                row[i] = (row[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                row[i] = (row[i] + paeth(left, up, up_left)) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"Unsupported PNG filter: {filter_type}")
        rows.append(bytes(row))
        prev = row
    return b"".join(rows)


def png_to_rgb(data: bytes) -> tuple[int, int, bytes]:
    width, height, _bit_depth, color_type, raw = parse_png(data)
    pixels = unfilter_png(width, height, color_type, raw)
    rgb = bytearray()
    if color_type == 0:
        for gray in pixels:
            rgb.extend((gray, gray, gray))
    elif color_type == 2:
        rgb.extend(pixels)
    elif color_type == 4:
        for i in range(0, len(pixels), 2):
            gray, alpha = pixels[i], pixels[i + 1]
            value = ((gray * alpha) + (255 * (255 - alpha))) // 255
            rgb.extend((value, value, value))
    elif color_type == 6:
        for i in range(0, len(pixels), 4):
            r, g, b, alpha = pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3]
            rgb.extend(
                (
                    ((r * alpha) + (255 * (255 - alpha))) // 255,
                    ((g * alpha) + (255 * (255 - alpha))) // 255,
                    ((b * alpha) + (255 * (255 - alpha))) // 255,
                )
            )
    return width, height, bytes(rgb)


def load_image(path: Path) -> PdfImage:
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        width, height = read_jpeg_size(data)
        return PdfImage(width, height, "/DeviceRGB", 8, data, "/DCTDecode")
    if suffix == ".png":
        width, height, rgb = png_to_rgb(data)
        return PdfImage(width, height, "/DeviceRGB", 8, zlib.compress(rgb), "/FlateDecode")
    raise ValueError(f"Unsupported image format: {path}")


def pdf_object(obj_id: int, body: bytes) -> bytes:
    return f"{obj_id} 0 obj\n".encode() + body + b"\nendobj\n"


def stream_object(obj_id: int, dictionary: str, data: bytes) -> bytes:
    header = f"{obj_id} 0 obj\n<< {dictionary} /Length {len(data)} >>\nstream\n".encode()
    return header + data + b"\nendstream\nendobj\n"


def write_pdf(deck_dir: Path, output: Path) -> list[SlideImage]:
    slides = find_slide_images(deck_dir)
    images = [load_image(slide.path) for slide in slides]

    objects: list[bytes] = []
    page_ids: list[int] = []
    next_id = 1
    catalog_id = next_id
    next_id += 1
    pages_id = next_id
    next_id += 1

    page_records: list[tuple[int, int, int, PdfImage]] = []
    for image in images:
        image_id = next_id
        next_id += 1
        content_id = next_id
        next_id += 1
        page_id = next_id
        next_id += 1
        page_ids.append(page_id)
        page_records.append((image_id, content_id, page_id, image))

    objects.append(pdf_object(catalog_id, f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()))
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(pdf_object(pages_id, f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()))

    for number, (image_id, content_id, page_id, image) in enumerate(page_records, start=1):
        image_dict = (
            f"/Type /XObject /Subtype /Image /Width {image.width} /Height {image.height} "
            f"/ColorSpace {image.color_space} /BitsPerComponent {image.bits} /Filter {image.filters}"
        )
        objects.append(stream_object(image_id, image_dict, image.data))
        content = f"q\n{image.width} 0 0 {image.height} 0 0 cm\n/Im{number} Do\nQ\n".encode()
        objects.append(stream_object(content_id, "", content))
        page = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {image.width} {image.height}] "
            f"/Resources << /XObject << /Im{number} {image_id} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        objects.append(pdf_object(page_id, page.encode()))

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        handle.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for obj in objects:
            offsets.append(handle.tell())
            handle.write(obj)
        xref_offset = handle.tell()
        handle.write(f"xref\n0 {len(objects) + 1}\n".encode())
        handle.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            handle.write(f"{offset:010d} 00000 n \n".encode())
        handle.write(
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
        )
    return slides


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge slide images into a PDF.")
    parser.add_argument("deck_dir", help="Directory containing NN-slide-*.png|jpg images")
    parser.add_argument("-o", "--output", help="Output PDF path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    deck_dir = Path(args.deck_dir).expanduser().resolve()
    output = Path(args.output).expanduser().resolve() if args.output else deck_dir / f"{deck_dir.name}.pdf"
    try:
        slides = write_pdf(deck_dir, output)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Created: {output}")
    print(f"Pages: {len(slides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
