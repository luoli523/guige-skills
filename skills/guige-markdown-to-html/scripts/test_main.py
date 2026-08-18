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

    def test_builtin_defaults_use_simple_github_dark_and_citations(self):
        options = main.resolve_options({})

        self.assertEqual(options.theme, "simple")
        self.assertEqual(options.code_theme, "github-dark")
        self.assertTrue(options.cite)

    def test_manifest_preserves_publication_metadata_and_assets(self):
        source = pathlib.Path("/tmp/article/index.md")
        result = main.render_markdown(
            """---
title: 发布测试
description: 摘要
author: 鬼哥
image: cover.webp
---
# 发布测试

![图表](chart.webp)
""",
            source,
            main.RenderOptions(),
        )

        manifest = main.build_manifest(result, source, pathlib.Path("/tmp/article/output.html"))

        self.assertEqual(manifest["schemaVersion"], 1)
        self.assertEqual(manifest["assetBaseDir"], str(source.parent.resolve()))
        self.assertEqual(manifest["title"], "发布测试")
        self.assertEqual(manifest["cover"], {
            "source": "cover.webp",
            "resolvedPath": str((source.parent / "cover.webp").resolve()),
        })
        self.assertEqual(manifest["contentImages"][0]["resolvedPath"], str((source.parent / "chart.webp").resolve()))

    def test_no_cite_override_disables_citations(self):
        options = main.resolve_options({}, cite=False)
        result = main.render_markdown("[参考](https://example.com)", pathlib.Path("/tmp/article.md"), options)

        self.assertFalse(options.cite)
        self.assertNotIn("参考链接", result.content_html)

    def test_manifest_uses_first_inline_image_as_cover_fallback(self):
        source = pathlib.Path("/tmp/article/index.md")
        result = main.render_markdown("![图表](chart.webp)", source, main.RenderOptions())

        manifest = main.build_manifest(result, source, pathlib.Path("/tmp/article.html"))

        self.assertEqual(manifest["cover"], {
            "source": "chart.webp",
            "resolvedPath": str((source.parent / "chart.webp").resolve()),
        })

    def test_render_highlights_supported_fenced_code_blocks(self):
        result = main.render_markdown(
            """```bash
git clone https://example.com/project.git
export APP_NAME=guige
```

```yaml
title: "测试"
enabled: true
```
""",
            pathlib.Path("/tmp/article.md"),
            main.RenderOptions(),
        )

        self.assertIn('class="hljs code__pre"', result.content_html)
        self.assertIn('class="language-bash"', result.content_html)
        self.assertIn('class="language-yaml"', result.content_html)
        self.assertIn("hljs-built-in", result.content_html)
        self.assertIn("hljs-attr", result.content_html)
        self.assertIn("&nbsp;", result.content_html)
        self.assertIn("<br>", result.content_html)

    def test_compact_output_avoids_repeated_inline_code_styles_and_highlighting(self):
        result = main.render_markdown(
            "正文含有 `inline`。\n\n```bash\ngit status\n```",
            pathlib.Path("/tmp/article.md"),
            main.RenderOptions(compact=True),
        )

        self.assertIn("<code>inline</code>", result.content_html)
        self.assertNotIn(main.CODE_STYLE, result.content_html)
        self.assertNotIn('class="hljs-', result.content_html)
        self.assertNotIn("● ● ●", result.content_html)

    def test_base_url_resolves_root_relative_links_without_citing_them(self):
        result = main.render_markdown(
            "[站内文章](/p/example/)",
            pathlib.Path("/tmp/article.md"),
            main.RenderOptions(cite=True, base_url="https://luoli523.github.io"),
        )

        self.assertIn('href="https://luoli523.github.io/p/example/"', result.content_html)
        self.assertNotIn("参考链接", result.content_html)


if __name__ == "__main__":
    unittest.main()
