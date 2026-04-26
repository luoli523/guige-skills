from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_svg.cli import render_command, template_command
from guige_svg.renderer import render_svg


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class RendererTests(unittest.TestCase):
    def test_render_matrix_contains_viewbox_and_title(self) -> None:
        spec = {
            "title": "Family Schedule",
            "type": "matrix",
            "sections": [
                {
                    "title": "Mon",
                    "items": [
                        {"label": "Child", "text": "5:45-6:30 Swim", "icon": "swim"},
                    ],
                }
            ],
        }
        svg = render_svg(spec)
        self.assertIn("<svg", svg)
        self.assertIn("viewBox=", svg)
        self.assertIn("Family Schedule", svg)

    def test_template_and_render_command_write_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            spec_path = temp / "spec.json"
            svg_path = temp / "out.svg"
            template_command(Args(type="matrix", output=str(spec_path)))
            result = render_command(
                Args(
                    spec=str(spec_path),
                    svg=str(svg_path),
                    theme=None,
                    png=False,
                    scale=2,
                    download=False,
                    json_output=True,
                )
            )

            self.assertTrue(svg_path.exists())
            self.assertTrue(result["success"])
            self.assertEqual(result["svg_path"], str(svg_path.resolve()))


if __name__ == "__main__":
    unittest.main()
