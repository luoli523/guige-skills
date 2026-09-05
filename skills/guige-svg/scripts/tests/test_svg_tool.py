from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_svg.cli import main, process_svg
from guige_svg.validate import validate_svg_text


VALID_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" role="img">
  <title>Request flow</title>
  <defs><marker id="arrow"><path d="M0 0L8 4L0 8Z"/></marker></defs>
  <rect x="20" y="30" width="120" height="50" rx="6"/>
  <path d="M140 55H250" marker-end="url(#arrow)"/>
  <text x="80" y="60">Client</text>
</svg>
"""


class SvgValidationTests(unittest.TestCase):
    def test_accepts_a_self_contained_responsive_svg(self) -> None:
        result = validate_svg_text(VALID_SVG)

        self.assertEqual(result["view_box"], [0.0, 0.0, 400.0, 240.0])
        self.assertEqual(result["title"], "Request flow")

    def test_rejects_executable_svg_content(self) -> None:
        unsafe = VALID_SVG.replace("</svg>", '<script>alert(1)</script><rect onclick="run()"/></svg>')

        with self.assertRaisesRegex(ValueError, "script"):
            validate_svg_text(unsafe)

    def test_rejects_external_resources_and_xml_entities(self) -> None:
        external = VALID_SVG.replace("</svg>", '<image href="https://example.com/a.png"/></svg>')
        entity = '<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>' + VALID_SVG

        with self.assertRaisesRegex(ValueError, "external resource"):
            validate_svg_text(external)
        with self.assertRaisesRegex(ValueError, "DOCTYPE|ENTITY"):
            validate_svg_text(entity)

    def test_rejects_external_urls_in_inline_styles_and_xml_stylesheets(self) -> None:
        inline_style = VALID_SVG.replace("<rect x=", '<rect style="fill:url(https://example.com/a.svg)" x=', 1)
        stylesheet = '<?xml-stylesheet href="https://example.com/theme.css"?>\n' + VALID_SVG

        with self.assertRaisesRegex(ValueError, "external resource"):
            validate_svg_text(inline_style)
        with self.assertRaisesRegex(ValueError, "stylesheet"):
            validate_svg_text(stylesheet)

    def test_rejects_fixed_dimensions_and_broken_references(self) -> None:
        fixed = VALID_SVG.replace("viewBox=", 'width="400" height="240" viewBox=')
        broken = VALID_SVG.replace("url(#arrow)", "url(#missing)")

        with self.assertRaisesRegex(ValueError, "width.*height"):
            validate_svg_text(fixed)
        with self.assertRaisesRegex(ValueError, "missing SVG id"):
            validate_svg_text(broken)

    def test_requires_image_semantics_and_valid_fragment_references(self) -> None:
        missing_role = VALID_SVG.replace(' role="img"', "")
        broken_fragment = VALID_SVG.replace("</svg>", '<use href="#missing"/></svg>')

        with self.assertRaisesRegex(ValueError, 'role="img"'):
            validate_svg_text(missing_role)
        with self.assertRaisesRegex(ValueError, "missing SVG id"):
            validate_svg_text(broken_fragment)

    def test_rejects_event_handlers_and_foreign_html(self) -> None:
        event_handler = VALID_SVG.replace("<rect x=", '<rect onload="run()" x=', 1)
        foreign_html = VALID_SVG.replace("</svg>", "<foreignObject><div>HTML</div></foreignObject></svg>")

        with self.assertRaisesRegex(ValueError, "event handler"):
            validate_svg_text(event_handler)
        with self.assertRaisesRegex(ValueError, "foreignobject"):
            validate_svg_text(foreign_html)


class SvgCliTests(unittest.TestCase):
    def test_validate_only_checks_an_agent_written_svg_without_exporting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_path = Path(temp_dir) / "diagram.svg"
            svg_path.write_text(VALID_SVG, encoding="utf-8")

            result = process_svg(svg_path, validate_only=True)

            self.assertTrue(result["success"])
            self.assertIsNone(result["png_path"])
            self.assertEqual(result["validation"]["title"], "Request flow")

    @patch("guige_svg.cli.export_png", return_value=None)
    def test_default_command_keeps_svg_when_png_converter_is_unavailable(self, _export_png) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_path = Path(temp_dir) / "diagram.svg"
            svg_path.write_text(VALID_SVG, encoding="utf-8")

            result = process_svg(svg_path)

            self.assertFalse(result["png_exported"])
            self.assertIn("PNG converter", result["warnings"][0])

    def test_json_cli_returns_a_machine_readable_validation_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch("builtins.print") as output:
            svg_path = Path(temp_dir) / "diagram.svg"
            svg_path.write_text(VALID_SVG, encoding="utf-8")

            exit_code = main([str(svg_path), "--validate-only", "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.call_args.args[0])
            self.assertEqual(payload["validation"]["title"], "Request flow")

    def test_refuses_to_overwrite_the_source_svg_with_png_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_path = Path(temp_dir) / "diagram.svg"
            svg_path.write_text(VALID_SVG, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must differ"):
                process_svg(svg_path, output_path=svg_path)
            self.assertEqual(svg_path.read_text(encoding="utf-8"), VALID_SVG)


if __name__ == "__main__":
    unittest.main()
