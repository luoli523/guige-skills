from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_imagen.providers import google, openai
from guige_imagen.types import CliArgs


class OpenAIProviderTests(unittest.TestCase):
    def test_openai_size_mapping(self) -> None:
        self.assertEqual(openai.get_openai_size("gpt-image-1.5", "16:9", "2k"), "1536x1024")
        self.assertEqual(openai.get_openai_size("gpt-image-1.5", "9:16", "2k"), "1024x1536")
        self.assertEqual(openai.get_openai_size("dall-e-3", "16:9", "2k"), "1792x1024")

    def test_openai_generations_body_for_gpt_image(self) -> None:
        args = CliArgs(aspect_ratio="16:9", quality="2k")
        body = openai.build_generations_body("A cat", "gpt-image-1.5", args)

        self.assertEqual(body["model"], "gpt-image-1.5")
        self.assertEqual(body["prompt"], "A cat")
        self.assertEqual(body["quality"], "high")
        self.assertEqual(body["size"], "1536x1024")
        self.assertNotIn("response_format", body)

    def test_openai_generations_body_for_dalle(self) -> None:
        args = CliArgs(aspect_ratio="1:1", quality="normal")
        body = openai.build_generations_body("A cat", "dall-e-3", args)

        self.assertEqual(body["quality"], "standard")
        self.assertEqual(body["response_format"], "b64_json")

    def test_extract_base64_image(self) -> None:
        payload = base64.b64encode(b"image-bytes").decode("ascii")
        self.assertEqual(openai.extract_image_from_response({"data": [{"b64_json": payload}]}), b"image-bytes")


class GoogleProviderTests(unittest.TestCase):
    def test_google_model_detection(self) -> None:
        self.assertTrue(google.is_imagen_model("imagen-4.0-generate-001"))
        self.assertFalse(google.is_imagen_model("gemini-3-pro-image-preview"))

    def test_extract_inline_image_data(self) -> None:
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "done"},
                            {"inlineData": {"data": "abc"}},
                        ]
                    }
                }
            ]
        }
        self.assertEqual(google.extract_inline_image_data(response), "abc")

    def test_extract_predicted_image_data(self) -> None:
        self.assertEqual(
            google.extract_predicted_image_data({"predictions": [{"image": {"imageBytes": "abc"}}]}),
            "abc",
        )

    def test_add_aspect_to_prompt(self) -> None:
        self.assertEqual(
            google.add_aspect_to_prompt("Draw a card", "16:9"),
            "Draw a card Aspect ratio: 16:9.",
        )


if __name__ == "__main__":
    unittest.main()
