from pathlib import Path

from guige_picbook.utils.config import SETTINGS_ENV_FILES, Settings


def test_settings_uses_skill_specific_env_files() -> None:
    env_files = Settings.model_config["env_file"]

    assert env_files == SETTINGS_ENV_FILES
    assert ".env" not in env_files
    assert str(Path.home() / ".guige-skills" / "guige-picbook" / ".env") in env_files
    assert ".guige-skills/guige-picbook/.env" in env_files
