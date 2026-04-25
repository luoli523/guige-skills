from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guige_imagen.config import (
    detect_provider,
    extract_yaml_frontmatter,
    get_extend_config_paths,
    get_model_for_provider,
    load_extend_config,
    parse_simple_yaml,
)
from guige_imagen.env import load_env_files
from guige_imagen.types import CliArgs, ExtendConfig


class ConfigTests(unittest.TestCase):
    def test_extract_and_parse_extend_config(self) -> None:
        content = """---
version: 1
default_provider: google
default_quality: 2k
default_aspect_ratio: "16:9"
default_image_size: 2K
default_model:
  google: "gemini-3-pro-image-preview"
  openai: "gpt-image-1.5"
---
"""
        yaml = extract_yaml_frontmatter(content)
        self.assertIsNotNone(yaml)
        config = parse_simple_yaml(yaml or "")

        self.assertEqual(config.default_provider, "google")
        self.assertEqual(config.default_quality, "2k")
        self.assertEqual(config.default_aspect_ratio, "16:9")
        self.assertEqual(config.default_image_size, "2K")
        self.assertEqual(config.default_model["google"], "gemini-3-pro-image-preview")
        self.assertEqual(config.default_model["openai"], "gpt-image-1.5")

    def test_extend_config_path_order(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            xdg = Path(root) / "xdg"
            cwd.mkdir()
            home.mkdir()
            xdg.mkdir()
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}, clear=False):
                paths = get_extend_config_paths(cwd, home)

        self.assertEqual(paths[0].name, "EXTEND.md")
        self.assertIn(".guige-skills/guige-imagen/EXTEND.md", str(paths[0]))
        self.assertIn("xdg/guige-skills/guige-imagen/EXTEND.md", str(paths[1]))
        self.assertIn("home/.guige-skills/guige-imagen/EXTEND.md", str(paths[2]))

    def test_load_project_extend_config_first(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            project_config = cwd / ".guige-skills" / "guige-imagen"
            home_config = home / ".guige-skills" / "guige-imagen"
            project_config.mkdir(parents=True)
            home_config.mkdir(parents=True)
            (project_config / "EXTEND.md").write_text(
                "---\ndefault_provider: google\n---\n", encoding="utf-8"
            )
            (home_config / "EXTEND.md").write_text(
                "---\ndefault_provider: openai\n---\n", encoding="utf-8"
            )

            config = load_extend_config(cwd, home)

        self.assertEqual(config.default_provider, "google")

    def test_load_env_files_clears_ambient_provider_env_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            cwd.mkdir()
            home.mkdir()

            with patch.dict(
                os.environ,
                {
                    "OPENAI_API_KEY": "ambient-openai",
                    "GOOGLE_API_KEY": "ambient-google",
                    "GEMINI_API_KEY": "ambient-gemini",
                    "OPENAI_BASE_URL": "https://ambient.example/v1",
                    "CUSTOM_ENV": "kept",
                },
                clear=True,
            ):
                load_env_files(cwd, home)
                self.assertNotIn("OPENAI_API_KEY", os.environ)
                self.assertNotIn("GOOGLE_API_KEY", os.environ)
                self.assertNotIn("GEMINI_API_KEY", os.environ)
                self.assertNotIn("OPENAI_BASE_URL", os.environ)
                self.assertEqual(os.environ["CUSTOM_ENV"], "kept")

    def test_load_env_files_prefers_project_provider_env(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            (cwd / ".guige-skills").mkdir(parents=True)
            (home / ".guige-skills").mkdir(parents=True)
            (home / ".guige-skills" / ".env").write_text("GOOGLE_API_KEY=home\n", encoding="utf-8")
            (cwd / ".guige-skills" / ".env").write_text("GOOGLE_API_KEY=cwd\n", encoding="utf-8")

            with patch.dict(os.environ, {"GOOGLE_API_KEY": "process"}, clear=True):
                load_env_files(cwd, home)
                self.assertEqual(os.environ["GOOGLE_API_KEY"], "cwd")

    def test_load_env_files_can_allow_ambient_provider_env(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            (cwd / ".guige-skills").mkdir(parents=True)
            (cwd / ".guige-skills" / ".env").write_text("GOOGLE_API_KEY=cwd\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {
                    "GUIGE_ALLOW_AMBIENT_PROVIDER_ENV": "1",
                    "GOOGLE_API_KEY": "process",
                },
                clear=True,
            ):
                load_env_files(cwd, home)
                self.assertEqual(os.environ["GOOGLE_API_KEY"], "process")

    def test_load_env_files_does_not_allow_ambient_provider_env_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            (cwd / ".guige-skills").mkdir(parents=True)
            (cwd / ".guige-skills" / ".env").write_text(
                "GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1\n", encoding="utf-8"
            )

            with patch.dict(os.environ, {"GOOGLE_API_KEY": "process"}, clear=True):
                load_env_files(cwd, home)
                self.assertNotIn("GOOGLE_API_KEY", os.environ)
                self.assertNotIn("GUIGE_ALLOW_AMBIENT_PROVIDER_ENV", os.environ)

    def test_load_env_files_keeps_non_provider_process_env_over_file_values(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root) / "project"
            home = Path(root) / "home"
            (cwd / ".guige-skills").mkdir(parents=True)
            (cwd / ".guige-skills" / ".env").write_text("CUSTOM_VALUE=file\n", encoding="utf-8")

            with patch.dict(os.environ, {"CUSTOM_VALUE": "process"}, clear=True):
                load_env_files(cwd, home)
                self.assertEqual(os.environ["CUSTOM_VALUE"], "process")

    def test_detect_provider_from_model_and_env(self) -> None:
        self.assertEqual(detect_provider(CliArgs(model="gpt-image-1.5")), "openai")
        self.assertEqual(detect_provider(CliArgs(model="gemini-3-pro-image-preview")), "google")

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "key"}, clear=True):
            self.assertEqual(detect_provider(CliArgs()), "google")

    def test_get_model_for_provider_priority(self) -> None:
        config = ExtendConfig()
        config.default_model["google"] = "configured-google"
        self.assertEqual(get_model_for_provider("google", "cli-model", config), "cli-model")
        self.assertEqual(get_model_for_provider("google", None, config), "configured-google")


if __name__ == "__main__":
    unittest.main()
