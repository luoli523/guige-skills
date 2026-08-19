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

    def test_render_adds_frontmatter_highlight_as_lead_callout(self):
        result = main.render_markdown(
            """---
title: 测试文章
description: 默认摘要
highlight: 这是 **关键价值**。
---
正文
""",
            pathlib.Path("/tmp/article.md"),
            main.RenderOptions(color="#009874"),
        )

        self.assertIn('<blockquote style="margin:0 0 1em;', result.content_html)
        self.assertIn('border-left:4px solid #009874', result.content_html)
        self.assertIn('<strong style="color:#009874;font-weight:bold;font-size:inherit;">关键价值</strong>', result.content_html)
        self.assertLess(result.content_html.index("关键价值"), result.content_html.index("正文"))

    def test_highlight_false_disables_the_lead_callout(self):
        result = main.render_markdown(
            """---
title: 测试文章
description: 默认摘要
highlight: false
---
正文
""",
            pathlib.Path("/tmp/article.md"),
            main.RenderOptions(),
        )

        self.assertNotIn("默认摘要", result.content_html)
        self.assertNotIn("<blockquote", result.content_html)

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

    def test_builtin_defaults_use_simple_github_and_citations(self):
        options = main.resolve_options({})

        self.assertEqual(options.theme, "simple")
        self.assertEqual(options.code_theme, "github")
        self.assertEqual(options.base_url, "https://luoli523.github.io")
        self.assertTrue(options.cite)

    def test_simple_theme_matches_legacy_wechat_visual_baseline(self):
        styles = main.style_map(main.resolve_options({}))

        self.assertIn("-apple-system-font", styles["article"])
        self.assertIn("line-height:1.75", styles["article"])
        self.assertIn("letter-spacing:0.1em", styles["p"])
        self.assertIn("margin:1.5em 8px", styles["p"])
        self.assertIn("background:#0F4C81", styles["h2"])
        self.assertIn("margin:4em auto 2em", styles["h2"])
        self.assertIn("border-width:2px 0 0", styles["hr"])
        self.assertIn("padding:0 !important", styles["pre"])
        self.assertEqual(styles["img"], "display:block;max-width:100%;margin:0.1em auto 0.5em;border-radius:4px;")
        self.assertEqual(main.CODE_STYLE, "font-size:90%;color:#d14;background:rgba(27,31,35,0.05);padding:3px 5px;border-radius:4px;")

    def test_simple_theme_uses_accent_for_table_headers_and_subheadings(self):
        styles = main.style_map(main.resolve_options({}))

        self.assertIn("background:#0F4C81", styles["th"])
        self.assertIn("color:#fff", styles["th"])
        self.assertIn("border-left:4px solid #0F4C81", styles["h3"])
        self.assertIn("background:rgba(15,76,129,0.08)", styles["h3"])

    def test_body_emphasis_uses_the_active_theme_color(self):
        result = main.render_markdown(
            "---\nhighlight: false\n---\n正文里的 **重点**。", pathlib.Path("/tmp/article.md"), main.RenderOptions(color="#009874")
        )

        self.assertIn('<strong style="color:#009874;font-weight:bold;font-size:inherit;">重点</strong>', result.content_html)

    def test_empty_base_url_config_falls_back_to_site_default(self):
        self.assertEqual(main.resolve_options({"base_url": ""}).base_url, "https://luoli523.github.io")

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
        self.assertEqual(manifest["contentSourceUrl"], "https://luoli523.github.io/p/article/")
        self.assertEqual(manifest["cover"], {
            "source": "cover.webp",
            "resolvedPath": str((source.parent / "cover.webp").resolve()),
        })
        self.assertEqual(manifest["contentImages"][0]["resolvedPath"], str((source.parent / "chart.webp").resolve()))

    def test_manifest_defaults_author_and_honors_explicit_source_url(self):
        source = pathlib.Path("/tmp/article/index.md")
        result = main.render_markdown(
            """---
title: 发布测试
slug: ignored-slug
content_source_url: /original/article/
---
正文
""",
            source,
            main.RenderOptions(),
        )

        manifest = main.build_manifest(result, source, pathlib.Path("/tmp/article/output.html"))

        self.assertEqual(result.author, "鬼哥")
        self.assertEqual(manifest["contentSourceUrl"], "https://luoli523.github.io/original/article/")

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
        self.assertIn('class="mac-sign"', result.content_html)
        self.assertIn('viewBox="0 0 450 130"', result.content_html)
        self.assertIn('fill="rgb(237,108,96)"', result.content_html)
        self.assertIn('fill="rgb(247,193,81)"', result.content_html)
        self.assertIn('fill="rgb(100,200,86)"', result.content_html)
        self.assertIn("font-size:90%", result.content_html)
        self.assertIn('class="language-bash" style="font-size:90%', result.content_html)
        self.assertNotIn("font-family:'Fira Code'", result.content_html)
        self.assertIn("color:#005cc5", result.content_html)
        self.assertNotIn("● ● ●", result.content_html)
        self.assertNotIn("<pre class=\"hljs code__pre\" style=\"" + main.style_map(main.RenderOptions())["pre"] + "\"><div", result.content_html)

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
