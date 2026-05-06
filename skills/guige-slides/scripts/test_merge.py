from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = Path(__file__).resolve().parent
merge_to_pptx = load_module("merge_to_pptx", BASE / "merge_to_pptx.py")
merge_to_pdf = load_module("merge_to_pdf", BASE / "merge_to_pdf.py")


def png_chunk(kind: bytes, data: bytes) -> bytes:
    import struct
    import zlib as _zlib

    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", _zlib.crc32(payload) & 0xFFFFFFFF)


def tiny_png(width: int = 2, height: int = 2) -> bytes:
    import struct

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    rows = []
    for _ in range(height):
        rows.append(b"\x00" + bytes([255, 0, 0] * width))
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(b"".join(rows)))
        + png_chunk(b"IEND", b"")
    )


class MergeTests(unittest.TestCase):
    def test_find_slide_images_sorts_by_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp)
            (deck / "02-slide-two.png").write_bytes(tiny_png())
            (deck / "01-slide-one.png").write_bytes(tiny_png())
            slides = merge_to_pptx.find_slide_images(deck)
            self.assertEqual([slide.filename for slide in slides], ["01-slide-one.png", "02-slide-two.png"])

    def test_merge_to_pptx_creates_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp)
            (deck / "01-slide-cover.png").write_bytes(tiny_png())
            out = deck / "deck.pptx"
            slides = merge_to_pptx.write_pptx(deck, out)
            self.assertEqual(len(slides), 1)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 1000)

    def test_merge_to_pdf_creates_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp)
            (deck / "01-slide-cover.png").write_bytes(tiny_png())
            out = deck / "deck.pdf"
            slides = merge_to_pdf.write_pdf(deck, out)
            self.assertEqual(len(slides), 1)
            self.assertTrue(out.exists())
            self.assertTrue(out.read_bytes().startswith(b"%PDF-1.4"))


if __name__ == "__main__":
    unittest.main()
