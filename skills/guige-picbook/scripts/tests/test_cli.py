"""CLI helper tests."""

from datetime import date
from pathlib import Path

from guige_picbook.cli import (
    _build_upload_command,
    _default_upload_target,
    _resolve_upload_target,
)


def test_default_upload_target_uses_runtime_year_month() -> None:
    assert _default_upload_target(date(2026, 5, 13)) == "drive:Rakuten Kobo/202605"


def test_resolve_upload_target_prefers_picbook_env(monkeypatch) -> None:
    monkeypatch.setenv("GUIGE_PICBOOK_DRIVE_TARGET", "drive:Custom/Picbook")
    monkeypatch.setenv("GUIGE_DRIVE_TARGET", "drive:Generic")

    assert _resolve_upload_target() == "drive:Custom/Picbook"


def test_resolve_upload_target_keeps_generic_override(monkeypatch) -> None:
    monkeypatch.delenv("GUIGE_PICBOOK_DRIVE_TARGET", raising=False)
    monkeypatch.setenv("GUIGE_DRIVE_TARGET", "drive:Generic")

    assert _resolve_upload_target() == "drive:Generic"


def test_build_upload_command_uses_monthly_task_layout() -> None:
    command = _build_upload_command(
        Path("/repo/skills/guige-drive-upload/scripts/main.py"),
        "世界主要国家",
        ["picbook/世界主要国家"],
        "drive:Rakuten Kobo/202605",
    )

    assert "--target" in command
    assert command[command.index("--target") + 1] == "drive:Rakuten Kobo/202605"
    assert "--layout" in command
    assert command[command.index("--layout") + 1] == "task"
