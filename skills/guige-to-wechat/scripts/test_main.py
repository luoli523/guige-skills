#!/usr/bin/env python3
import unittest

import main


class GuigeToWechatTests(unittest.TestCase):
    def test_parse_frontmatter_extracts_fields_and_body(self):
        frontmatter, body = main.parse_frontmatter(
            """---
title: "测试标题"
tags:
  - AI
  - 微信
author: 鬼哥
---
# 正文标题

第一段内容。
"""
        )

        self.assertEqual(frontmatter["title"], "测试标题")
        self.assertEqual(frontmatter["tags"], ["AI", "微信"])
        self.assertEqual(frontmatter["author"], "鬼哥")
        self.assertIn("第一段内容", body)

    def test_parse_extend_config_with_default_account(self):
        config = main.parse_extend_config(
            """default_theme: simple
default_color: teal
default_code_theme: github
mac_code_block: 0
default_author: 鬼哥
need_open_comment: 0
only_fans_can_comment: 1

accounts:
  - name: 鬼哥公众号
    alias: guige
    default: true
    app_id: wx123
    app_secret: secret
"""
        )
        account = main.resolve_account(config)

        self.assertEqual(config.default_theme, "simple")
        self.assertEqual(config.default_color, "teal")
        self.assertEqual(config.default_code_theme, "github")
        self.assertFalse(config.mac_code_block)
        self.assertEqual(config.need_open_comment, 0)
        self.assertEqual(config.only_fans_can_comment, 1)
        self.assertEqual(account.alias, "guige")
        self.assertEqual(account.app_id, "wx123")
        self.assertEqual(account.default_author, "鬼哥")

    def test_markdown_renderer_tracks_images_and_citations(self):
        renderer = main.MarkdownRenderer(theme="default", color="blue", cite=True)
        rendered = renderer.render(
            """# 标题

这是一段包含 [OpenAI](https://openai.com) 的文字。

![封面](imgs/cover.png)

| 项目 | 状态 |
| --- | --- |
| 测试 | 通过 |
"""
        )

        self.assertIn("<h1", rendered)
        self.assertIn("参考链接", rendered)
        self.assertIn("https://openai.com", rendered)
        self.assertIn('src="imgs/cover.png"', rendered)
        self.assertIn("<table", rendered)
        self.assertEqual(renderer.inline_images, ["imgs/cover.png"])

    def test_markdown_renderer_formats_fenced_code_blocks(self):
        renderer = main.MarkdownRenderer(theme="default", color="green", cite=False)
        rendered = renderer.render(
            """```bash
git clone https://github.com/luoli523/ai-convo-exporter
export VAULT_DIR="$HOME/Documents/Obsidian Vault"
```

```yaml
---
title: AI 对话沉淀
tags:
  - AI
---
```
"""
        )

        self.assertIn('class="hljs code__pre"', rendered)
        self.assertIn('class="language-bash"', rendered)
        self.assertIn('class="language-yaml"', rendered)
        self.assertIn("mac-sign", rendered)
        self.assertIn("&nbsp;", rendered)
        self.assertIn("<br>", rendered)
        self.assertIn("hljs-built-in", rendered)
        self.assertIn("hljs-attr", rendered)

    def test_markdown_renderer_can_disable_mac_code_header(self):
        renderer = main.MarkdownRenderer(theme="default", color="green", cite=False, mac_code_block=False)
        rendered = renderer.render("```bash\ngit status\n```")

        self.assertIn('class="hljs code__pre"', rendered)
        self.assertNotIn("mac-sign", rendered)

    def test_green_color_matches_wechat_theme_reference(self):
        self.assertEqual(main.resolve_color("green"), "#009874")

    def test_build_news_article_payload(self):
        article = main.build_draft_article(
            title="标题",
            author="鬼哥",
            digest="摘要",
            content="<p>正文</p>",
            thumb_media_id="media123",
            article_type="news",
            image_media_ids=[],
            need_open_comment=1,
            only_fans_can_comment=0,
        )

        self.assertEqual(article["article_type"], "news")
        self.assertEqual(article["thumb_media_id"], "media123")
        self.assertEqual(article["digest"], "摘要")
        self.assertEqual(article["author"], "鬼哥")

    def test_build_newspic_article_payload(self):
        article = main.build_draft_article(
            title="图片消息",
            author="",
            digest="",
            content="<p>正文</p>",
            thumb_media_id="",
            article_type="newspic",
            image_media_ids=["img1", "img2"],
            need_open_comment=0,
            only_fans_can_comment=0,
        )

        self.assertEqual(article["article_type"], "newspic")
        self.assertEqual(
            article["image_info"],
            {"image_list": [{"image_media_id": "img1"}, {"image_media_id": "img2"}]},
        )
        self.assertNotIn("author", article)

    def test_news_requires_cover_media_id(self):
        with self.assertRaises(main.WechatError):
            main.build_draft_article(
                title="标题",
                author="",
                digest="",
                content="<p>正文</p>",
                thumb_media_id="",
                article_type="news",
                image_media_ids=[],
                need_open_comment=1,
                only_fans_can_comment=0,
            )

    def test_validate_news_requires_cover_or_inline_image(self):
        rendered = main.RenderResult(
            title="标题",
            summary="",
            author="",
            html_content="<section><p>正文</p></section>",
            html_path="/tmp/out.html",
            frontmatter={},
            inline_images=[],
            source_path="/tmp/in.md",
            base_dir="/tmp",
        )

        with self.assertRaises(main.WechatError):
            main.validate_article_inputs(rendered, "news", "")


if __name__ == "__main__":
    unittest.main()
