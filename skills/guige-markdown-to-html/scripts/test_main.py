import importlib.util
import pathlib
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("main.py")
SPEC = importlib.util.spec_from_file_location("guige_markdown_to_html", SCRIPT)
main = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(main)


class MarkdownToHtmlTests(unittest.TestCase):
    def test_render_extracts_metadata_and_removes_document_title(self):
        markdown = """---
title: 测试文章
author: 鬼哥
description: 一段摘要
---
# 测试文章

正文包含 **重点** 和 [参考](https://example.com)。

## 第二节
"""
        result = main.render_markdown(markdown, pathlib.Path("/tmp/article.md"), main.RenderOptions(cite=True))

        self.assertEqual(result.title, "测试文章")
        self.assertEqual(result.author, "鬼哥")
        self.assertEqual(result.summary, "一段摘要")
        self.assertNotIn(">测试文章</h1>", result.content_html)
        self.assertIn("参考链接", result.content_html)
        self.assertIn("<strong", result.content_html)
        self.assertIn("<h2", result.content_html)

    def test_render_collects_relative_image_manifest(self):
        markdown = "![图表](imgs/chart.png)"
        source = pathlib.Path("/tmp/article/article.md")

        result = main.render_markdown(markdown, source, main.RenderOptions())

        self.assertEqual(result.content_images, [{
            "source": "imgs/chart.png",
            "resolvedPath": str((source.parent / "imgs/chart.png").resolve()),
            "alt": "图表",
        }])
        self.assertIn('src="imgs/chart.png"', result.content_html)

    def test_config_and_cli_options_override_defaults(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = pathlib.Path(temporary_directory) / "EXTEND.md"
            config_path.write_text("default_theme: grace\ndefault_font_size: 17\ncite: true\n", "utf-8")
            config = main.parse_config(config_path.read_text("utf-8"))

        options = main.resolve_options(config, theme="modern", font_size=None, cite=None)
        self.assertEqual(options.theme, "modern")
        self.assertEqual(options.font_size, "17px")
        self.assertTrue(options.cite)

    def test_builtin_defaults_use_modern_monokai_and_citations(self):
        options = main.resolve_options({})

        self.assertEqual(options.theme, "modern")
        self.assertEqual(options.code_theme, "monokai")
        self.assertTrue(options.cite)


if __name__ == "__main__":
    unittest.main()
