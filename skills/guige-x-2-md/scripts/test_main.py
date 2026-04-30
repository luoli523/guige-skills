#!/usr/bin/env python3
import unittest

import main


class XToMarkdownPureLogicTests(unittest.TestCase):
    def test_parse_ids(self):
        self.assertEqual(main.parse_tweet_id("https://x.com/user/status/12345?s=20"), "12345")
        self.assertEqual(main.parse_tweet_id("https://twitter.com/user/statuses/67890"), "67890")
        self.assertEqual(main.parse_article_id("https://x.com/i/article/111222333"), "111222333")
        self.assertEqual(main.parse_tweet_username("https://x.com/some_user/status/12345"), "some_user")

    def test_format_thread_tweets_markdown_includes_media_and_quote(self):
        quoted = {
            "rest_id": "9",
            "core": {"user_results": {"result": {"legacy": {"screen_name": "quoted", "name": "Quoted User"}}}},
            "legacy": {"full_text": "quoted text"},
        }
        tweet = {
            "rest_id": "1",
            "legacy": {
                "id_str": "1",
                "full_text": "hello\nworld",
                "extended_entities": {
                    "media": [
                        {
                            "type": "photo",
                            "media_url_https": "https://pbs.twimg.com/media/example.jpg",
                            "ext_alt_text": "Example image",
                        },
                        {
                            "type": "video",
                            "media_url_https": "https://pbs.twimg.com/media/poster.jpg",
                            "video_info": {
                                "variants": [
                                    {"content_type": "application/x-mpegURL", "url": "https://video.twimg.com/playlist.m3u8"},
                                    {
                                        "content_type": "video/mp4",
                                        "bitrate": 832000,
                                        "url": "https://video.twimg.com/video.mp4",
                                    },
                                ]
                            },
                        },
                    ]
                },
            },
            "quoted_status_result": {"result": quoted},
        }
        markdown = main.format_thread_tweets_markdown([tweet], username="author")
        self.assertIn("## 1", markdown)
        self.assertIn("https://x.com/author/status/1", markdown)
        self.assertIn("hello\nworld", markdown)
        self.assertIn("> Author: Quoted User (@quoted)", markdown)
        self.assertIn("![Example image](https://pbs.twimg.com/media/example.jpg)", markdown)
        self.assertIn("[video](https://video.twimg.com/video.mp4)", markdown)

    def test_format_article_markdown_renders_blocks_and_atomic_markdown(self):
        article = {
            "title": "Atomic Markdown Example",
            "content_state": {
                "blocks": [
                    {"type": "unstyled", "text": "Before the snippet.", "entityRanges": []},
                    {"type": "atomic", "text": " ", "entityRanges": [{"key": 0, "offset": 0, "length": 1}]},
                    {"type": "unordered-list-item", "text": "A list item", "entityRanges": []},
                ],
                "entityMap": {
                    "0": {
                        "key": "5",
                        "value": {
                            "type": "MARKDOWN",
                            "data": {"markdown": "```python\nprint('hello')\n```\n"},
                        },
                    }
                },
            },
        }
        markdown, cover = main.format_article_markdown(article)
        self.assertIsNone(cover)
        self.assertEqual(
            markdown,
            "# Atomic Markdown Example\n\nBefore the snippet.\n\n```python\nprint('hello')\n```\n\n- A list item",
        )

    def test_media_link_rewrite_includes_cover_image(self):
        markdown = (
            "---\n"
            'coverImage: "https://pbs.twimg.com/media/cover.jpg"\n'
            "---\n\n"
            "![Alt](https://pbs.twimg.com/media/img.jpg)\n"
            "[video](https://video.twimg.com/video.mp4)"
        )
        rewritten = main.rewrite_markdown_media_links(
            markdown,
            {
                "https://pbs.twimg.com/media/cover.jpg": "imgs/img-001-cover.jpg",
                "https://pbs.twimg.com/media/img.jpg": "imgs/img-002-img.jpg",
                "https://video.twimg.com/video.mp4": "videos/video-001-video.mp4",
            },
        )
        self.assertIn('coverImage: "imgs/img-001-cover.jpg"', rewritten)
        self.assertIn("![Alt](imgs/img-002-img.jpg)", rewritten)
        self.assertIn("[video](videos/video-001-video.mp4)", rewritten)


if __name__ == "__main__":
    unittest.main()
