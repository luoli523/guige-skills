from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("main.py")
SPEC = importlib.util.spec_from_file_location("guige_video_download_main", MODULE_PATH)
assert SPEC is not None
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class VideoDownloadTests(unittest.TestCase):
    def test_identify_platform(self) -> None:
        self.assertEqual(module.identify_platform("https://www.youtube.com/watch?v=abc"), "youtube")
        self.assertEqual(module.identify_platform("https://youtu.be/abc"), "youtube")
        self.assertEqual(module.identify_platform("https://x.com/user/status/123"), "x")
        self.assertEqual(module.identify_platform("https://twitter.com/user/status/123"), "x")

    def test_extract_url_id(self) -> None:
        self.assertEqual(module.extract_url_id("https://www.youtube.com/watch?v=abc123"), "abc123")
        self.assertEqual(module.extract_url_id("https://x.com/user/status/1234567890"), "1234567890")
        self.assertEqual(module.extract_url_id("https://www.youtube.com/shorts/shortid"), "shortid")

    def test_format_selector_audio(self) -> None:
        self.assertEqual(module.build_format_selector("audio", "mp4", audio_only=True), "bestaudio/best")

    def test_format_selector_quality_cap(self) -> None:
        selector = module.build_format_selector("1080p", "mp4")
        self.assertIn("height<=1080", selector)
        self.assertIn("ext=mp4", selector)

    def test_slugify(self) -> None:
        self.assertEqual(module.slugify("Hello, 世界!"), "hello-世界")
        self.assertEqual(module.slugify(""), "item")


if __name__ == "__main__":
    unittest.main()
