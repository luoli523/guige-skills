from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import importlib.util
import sys

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "main.py"
SPEC = importlib.util.spec_from_file_location("guige_drive_upload_main", SCRIPT_PATH)
assert SPEC and SPEC.loader
main = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = main
SPEC.loader.exec_module(main)


class DriveUploadTests(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(main.slugify("Python CLI Pipeline"), "python-cli-pipeline")
        self.assertEqual(main.slugify("生成一张鬼哥信息图"), "生成一张鬼哥信息图")
        self.assertEqual(main.slugify("!!!", "fallback"), "fallback")

    def test_join_remote(self) -> None:
        self.assertEqual(
            main.join_remote("gdrive:", "/guige-skills/", "guige-imagen"),
            "gdrive:guige-skills/guige-imagen",
        )

    def test_build_upload_plan_for_file_and_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image = root / "diagram.png"
            folder = root / "materials"
            image.write_bytes(b"png")
            folder.mkdir()

            plan = main.build_upload_plan(
                [str(image), str(folder)],
                "guige-infographic",
                "Python CLI Pipeline",
                "gdrive:",
            )

        self.assertEqual(
            plan.drive_folder,
            "gdrive:guige-skills/guige-infographic/python-cli-pipeline",
        )
        self.assertEqual(plan.items[0].destination, f"{plan.drive_folder}/diagram.png")
        self.assertFalse(plan.items[0].is_dir)
        self.assertEqual(plan.items[1].destination, f"{plan.drive_folder}/materials")
        self.assertTrue(plan.items[1].is_dir)


if __name__ == "__main__":
    unittest.main()
