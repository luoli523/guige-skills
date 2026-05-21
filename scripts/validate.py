#!/usr/bin/env python3
"""Validate guige-skills repository structure and conventions.

Checks
------
1. Every skills/<name>/SKILL.md exists and has YAML frontmatter.
2. Frontmatter contains non-empty 'name' and 'description'.
3. The 'name' field matches the containing directory name.
4. The 3 plugin manifests have synchronized 'name' and 'version'.
5. The 'skills' path declared in .claude-plugin/plugin.json exists.
6. Shell scripts in hooks/ and skills/<name>/scripts/ have +x bit.

Exit 0 on success, 1 on any violation.

Run locally:
    python3 scripts/validate.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    """Return YAML frontmatter as a flat dict of string scalars, or None if absent."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue
        mm = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if not mm:
            continue
        key, val = mm.group(1), mm.group(2).strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        fm[key] = val
    return fm


def check_skills() -> int:
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        fail(f"missing skills/ directory at {rel(skills_dir)}")
        return 0
    count = 0
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        count += 1
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            fail(f"missing SKILL.md: {rel(skill_dir)}/SKILL.md")
            continue
        fm = parse_frontmatter(skill_md)
        if fm is None:
            fail(f"no YAML frontmatter: {rel(skill_md)}")
            continue
        name = fm.get("name", "").strip()
        desc = fm.get("description", "").strip()
        if not name:
            fail(f"missing or empty 'name' field: {rel(skill_md)}")
        elif name != skill_dir.name:
            fail(
                f"name mismatch: {rel(skill_md)} has name='{name}', "
                f"expected '{skill_dir.name}'"
            )
        if not desc:
            fail(f"missing or empty 'description' field: {rel(skill_md)}")
    return count


def check_manifests() -> None:
    claude_plugin = ROOT / ".claude-plugin" / "plugin.json"
    claude_market = ROOT / ".claude-plugin" / "marketplace.json"
    codex_plugin = ROOT / ".codex-plugin" / "plugin.json"
    agents_market = ROOT / ".agents" / "plugins" / "marketplace.json"

    for p in (claude_plugin, claude_market, codex_plugin, agents_market):
        if not p.is_file():
            fail(f"missing manifest: {rel(p)}")
            return

    try:
        cdata = json.loads(claude_plugin.read_text(encoding="utf-8"))
        cmdata = json.loads(claude_market.read_text(encoding="utf-8"))
        xdata = json.loads(codex_plugin.read_text(encoding="utf-8"))
        adata = json.loads(agents_market.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"manifest is not valid JSON: {e}")
        return

    a_plugins = adata.get("plugins") or []
    a_plugin = a_plugins[0] if a_plugins else {}

    # Plugin name must sync across the 3 manifests that declare a plugin name.
    names = {
        ".claude-plugin/plugin.json": cdata.get("name"),
        ".codex-plugin/plugin.json": xdata.get("name"),
        ".agents/plugins/marketplace.json (plugins[0].name)": a_plugin.get("name"),
    }
    if len({v for v in names.values() if v is not None}) > 1 or None in names.values():
        fail(f"plugin 'name' out of sync across manifests: {names}")

    # Version sync: the two plugin.json files plus claude marketplace metadata.
    # .agents marketplace schema has no version field — intentionally excluded.
    versions = {
        ".claude-plugin/plugin.json": cdata.get("version"),
        ".claude-plugin/marketplace.json (metadata.version)": cmdata.get(
            "metadata", {}
        ).get("version"),
        ".codex-plugin/plugin.json": xdata.get("version"),
    }
    if (
        len({v for v in versions.values() if v is not None}) > 1
        or None in versions.values()
    ):
        fail(f"plugin 'version' out of sync across manifests: {versions}")

    skills_path = cdata.get("skills")
    if skills_path:
        full = (ROOT / skills_path).resolve()
        if not full.is_dir():
            fail(
                f".claude-plugin/plugin.json 'skills' path does not exist: "
                f"{skills_path}"
            )


def check_executable_bits() -> int:
    targets: list[Path] = []
    hooks_dir = ROOT / "hooks"
    if hooks_dir.is_dir():
        targets.extend(sorted(hooks_dir.glob("*.sh")))
    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
        targets.extend(sorted(skills_dir.glob("*/scripts/*.sh")))
    for sh in targets:
        if not os.access(sh, os.X_OK):
            fail(f"script missing executable bit (run chmod +x): {rel(sh)}")
    return len(targets)


def main() -> int:
    skill_count = check_skills()
    check_manifests()
    sh_count = check_executable_bits()

    if errors:
        print(f"FAIL: {len(errors)} error(s)\n", file=sys.stderr)
        for e in errors:
            print(f"  error: {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {skill_count} skills, 3 manifests synced, "
        f"{sh_count} shell script(s) executable"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
