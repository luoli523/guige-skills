from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_imagen.cli import parse_args


class CliTests(unittest.TestCase):
    def test_parse_basic_args(self) -> None:
        args = parse_args(
            [
                "--prompt",
                "A cat",
                "--image",
                "cat.png",
                "--provider",
                "openai",
                "--model",
                "gpt-image-1.5",
                "--ar",
                "16:9",
                "--quality",
                "2k",
                "--json",
            ]
        )

        self.assertEqual(args.prompt, "A cat")
        self.assertEqual(args.image_path, "cat.png")
        self.assertEqual(args.provider, "openai")
        self.assertEqual(args.model, "gpt-image-1.5")
        self.assertEqual(args.aspect_ratio, "16:9")
        self.assertEqual(args.quality, "2k")
        self.assertTrue(args.json_output)

    def test_parse_promptfiles_and_refs(self) -> None:
        args = parse_args(
            [
                "--promptfiles",
                "a.md",
                "b.md",
                "--ref",
                "one.png",
                "two.jpg",
                "--image",
                "out",
            ]
        )

        self.assertEqual(args.prompt_files, ["a.md", "b.md"])
        self.assertEqual(args.reference_images, ["one.png", "two.jpg"])
        self.assertEqual(args.image_path, "out")

    def test_image_is_optional_because_downloads_path_is_automatic(self) -> None:
        args = parse_args(["--prompt", "A cat"])

        self.assertEqual(args.prompt, "A cat")
        self.assertIsNone(args.image_path)


if __name__ == "__main__":
    unittest.main()
