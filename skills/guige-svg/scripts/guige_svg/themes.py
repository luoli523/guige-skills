from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    grid: str
    text: str
    muted: str
    stroke: str
    accent: str
    highlight: str
    card_fills: tuple[str, ...]


THEMES: dict[str, Theme] = {
    "guige-light": Theme(
        name="guige-light",
        background="#F5F0E8",
        grid="#E7DED2",
        text="#111111",
        muted="#6B6B6B",
        stroke="#111111",
        accent="#E8655A",
        highlight="#22A7A0",
        card_fills=("#A8D8EA", "#B5E5CF", "#D5C6E0", "#F4C7AB", "#F6E7A8"),
    ),
    "dark-tech": Theme(
        name="dark-tech",
        background="#0F172A",
        grid="#1E293B",
        text="#F8FAFC",
        muted="#94A3B8",
        stroke="#64748B",
        accent="#22D3EE",
        highlight="#34D399",
        card_fills=("#083344", "#064E3B", "#4C1D95", "#78350F", "#1E293B"),
    ),
}


def get_theme(name: str | None) -> Theme:
    if not name:
        return THEMES["guige-light"]
    if name not in THEMES:
        choices = ", ".join(sorted(THEMES))
        raise ValueError(f"Unknown theme: {name}. Choices: {choices}")
    return THEMES[name]
