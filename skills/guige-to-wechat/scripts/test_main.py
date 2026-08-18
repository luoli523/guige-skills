#!/usr/bin/env python3
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import main


class GuigeToWechatTests(unittest.TestCase):
    def test_parse_extend_config_keeps_channel_settings(self):
        config = main.parse_extend_config(
            """need_open_comment: 0
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

        self.assertEqual(config.need_open_comment, 0)
        self.assertEqual(config.only_fans_can_comment, 1)
        self.assertEqual(account.alias, "guige")
        self.assertEqual(account.app_id, "wx123")

    def test_load_render_manifest_uses_resolved_assets(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            html_path = root / "article.html"
            html_path.write_text("<html><body><section><img src=\"chart.webp\"></section></body></html>", "utf-8")
            manifest_path = root / "article.wechat.json"
            manifest_path.write_text(json.dumps({
                "schemaVersion": 1,
                "htmlPath": str(html_path),
                "assetBaseDir": str(root),
                "title": "测试标题",
                "summary": "测试摘要",
                "author": "鬼哥",
                "contentSourceUrl": "https://luoli523.github.io/p/test/",
                "cover": {"source": "cover.webp", "resolvedPath": str((root / "cover.webp").resolve())},
                "contentImages": [{"source": "chart.webp", "resolvedPath": str((root / "chart.webp").resolve()), "alt": "图表"}],
            }, ensure_ascii=False), "utf-8")

            rendered = main.load_render_manifest(manifest_path, output_html="")

            self.assertEqual(rendered.title, "测试标题")
            self.assertEqual(rendered.content_source_url, "https://luoli523.github.io/p/test/")
            self.assertEqual(rendered.base_dir, str(root.resolve()))
            self.assertEqual(rendered.cover_source, str((root / "cover.webp").resolve()))
            self.assertEqual(rendered.inline_images, [str((root / "chart.webp").resolve())])
            self.assertIn("<section>", rendered.html_content)

    def test_load_render_manifest_rejects_unsupported_schema(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = pathlib.Path(temporary_directory) / "article.wechat.json"
            path.write_text(json.dumps({"schemaVersion": 2}), "utf-8")

            with self.assertRaisesRegex(main.WechatError, "schemaVersion"):
                main.load_render_manifest(path, output_html="")

    def test_build_news_article_payload(self):
        article = main.build_draft_article(
            title="标题", author="鬼哥", digest="摘要", content="<p>正文</p>", thumb_media_id="media123",
            content_source_url="https://luoli523.github.io/p/test/", article_type="news", image_media_ids=[], need_open_comment=1, only_fans_can_comment=0,
        )

        self.assertEqual(article["article_type"], "news")
        self.assertEqual(article["thumb_media_id"], "media123")
        self.assertEqual(article["digest"], "摘要")
        self.assertEqual(article["author"], "鬼哥")
        self.assertEqual(article["content_source_url"], "https://luoli523.github.io/p/test/")

    def test_build_newspic_article_payload(self):
        article = main.build_draft_article(
            title="图片消息", author="", digest="", content="<p>正文</p>", thumb_media_id="",
            content_source_url="", article_type="newspic", image_media_ids=["img1", "img2"], need_open_comment=0, only_fans_can_comment=0,
        )

        self.assertEqual(article["image_info"], {"image_list": [{"image_media_id": "img1"}, {"image_media_id": "img2"}]})

    def test_validate_news_requires_cover_or_inline_image(self):
        rendered = main.PublicationInput(
            title="标题", summary="", author="", content_source_url="", html_content="<section><p>正文</p></section>",
            html_path="/tmp/out.html", cover_source="", inline_images=[], source_path="/tmp/in.json", base_dir="/tmp",
        )

        with self.assertRaises(main.WechatError):
            main.validate_article_inputs(rendered, "news", "")

    def test_prepare_cover_keeps_jpeg_and_png_unchanged(self):
        for filename, content_type in (("cover.jpg", "image/jpeg"), ("cover.png", "image/png")):
            asset = main.UploadAsset(b"image", filename, content_type, filename)
            with mock.patch.object(main, "convert_to_jpeg") as convert:
                self.assertIs(main.prepare_cover_asset(asset), asset)
                convert.assert_not_called()

    def test_prepare_cover_converts_webp_to_jpeg(self):
        source = main.UploadAsset(b"RIFFxxxxWEBP", "cover.webp", "image/webp", "cover.webp")
        converted = main.UploadAsset(b"jpeg", "cover.jpg", "image/jpeg", "cover.webp")
        with mock.patch.object(main, "convert_to_jpeg", return_value=converted) as convert:
            self.assertIs(main.prepare_cover_asset(source), converted)
            convert.assert_called_once_with(source, max_size=None)


if __name__ == "__main__":
    unittest.main()
