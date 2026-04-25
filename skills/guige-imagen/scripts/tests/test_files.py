from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_imagen import files


class FileTests(unittest.TestCase):
    def test_slugify_content_uses_heading_when_present(self) -> None:
        self.assertEqual(
            files.slugify_content("# Product Launch Diagram\n\nDraw a chart"),
            "product-launch-diagram",
        )

    def test_slugify_content_keeps_content_words(self) -> None:
        self.assertEqual(
            files.slugify_content("Create a clean photo of a translucent keyboard"),
            "clean-translucent-keyboard",
        )

    def test_slugify_content_handles_cjk_text(self) -> None:
        self.assertEqual(files.slugify_content("生成一张鬼哥信息图"), "生成一张鬼哥信息图")

    def test_resolve_download_output_path_uses_target_dir_and_requested_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir)
            with patch.object(files, "DEFAULT_IMAGE_OUTPUT_DIR", target_dir):
                path = files.resolve_download_output_path(
                    "A technical map of Python image generation",
                    "ignored-name.jpg",
                )

        self.assertEqual(path.name, "technical-map-python.jpg")

    def test_resolve_download_output_path_dedupes_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir)
            existing = target_dir / "cat.png"
            existing.write_bytes(b"existing")
            with patch.object(files, "DEFAULT_IMAGE_OUTPUT_DIR", target_dir):
                path = files.resolve_download_output_path("A cat")

        self.assertEqual(path.name, "cat-2.png")


if __name__ == "__main__":
    unittest.main()
