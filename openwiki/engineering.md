# Engineering guide: source map, validation, and operations

[← Quickstart](quickstart.md) · [Architecture](architecture/overview.md)

## Source map

| Location | Why it matters |
|---|---|
| `README.md` | User-facing catalog, examples, and broad product positioning |
| `CLAUDE.md` / `AGENTS.md` | Repository conventions, boundaries, local install/test commands; `AGENTS.md` was added as a symlink-compatible alias in the latest inspected commit |
| `skills/*/SKILL.md` | Canonical workflow and safety contract for every skill |
| `skills/*/references/` | Prompt templates, visual style guidance, configurations, troubleshooting, and product-specific policy |
| `skills/*/scripts/` | Deterministic CLIs/implementations and focused tests where a workflow needs code |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | Platform distribution declarations that must remain consistent |
| `hooks/` | Claude SessionStart registration and skill quick-reference shell hook |
| `install.sh` | Symlink installer, discovery, install-status, and stale-link cleanup logic |
| `scripts/validate.py` | Repository-wide structural gate |
| `scripts/download_to_drive.py` | Separate comic-to-PDF/rclone operational tool; not the generic Drive service |
| `.github/workflows/validate.yml` | Python 3.11 structural validation on main pushes and pull requests |

## Quality gates

### Required structural gate

```bash
python3 scripts/validate.py
```

The validator is intentionally small and dependency-free. It checks:

1. every immediate `skills/<name>/` directory has `SKILL.md` with YAML frontmatter;
2. `name` and `description` are non-empty, and `name` matches its directory;
3. plugin name synchronization across Claude, Codex, and Agents manifests;
4. version synchronization across the two plugin manifests and Claude marketplace metadata;
5. the Claude manifest’s declared skill path exists; and
6. executable bits for `hooks/*.sh` and immediate `skills/*/scripts/*.sh`.

GitHub Actions runs this check on `push` to `main` and on pull requests with Python 3.11 (`.github/workflows/validate.yml`). It does not run every skill’s tests or call external providers.

### Focused test map

Use the suite nearest the modified implementation; avoid live network/provider tests unless a contract explicitly provides a controlled path.

| Area | Test location | Typical command |
|---|---|---|
| Imagen CLI/config/files/providers | `skills/guige-imagen/scripts/tests/` | `python3 -m pytest skills/guige-imagen/scripts/tests` |
| Drive upload | `skills/guige-drive-upload/scripts/tests/test_main.py` | `python3 -m pytest skills/guige-drive-upload/scripts/tests` |
| Picbook CLI/config/content/generator/search/models | `skills/guige-picbook/scripts/tests/` | `python3 -m pytest skills/guige-picbook/scripts/tests` |
| SVG renderer | `skills/guige-svg/scripts/tests/test_renderer.py` | `python3 -m pytest skills/guige-svg/scripts/tests` |
| Slides merge | `skills/guige-slides/scripts/test_merge.py` | `python3 -m unittest skills/guige-slides/scripts/test_merge.py` |
| WeChat renderer/config/payload | `skills/guige-to-wechat/scripts/test_main.py` | `python3 -m unittest skills/guige-to-wechat/scripts/test_main.py` |
| Video parsing/format selection | `skills/guige-video-download/scripts/test_main.py` | `python3 -m unittest skills/guige-video-download/scripts/test_main.py` |
| X URL/Markdown/media transforms | `skills/guige-x-2-md/scripts/test_main.py` | `python3 -m unittest skills/guige-x-2-md/scripts/test_main.py` |

Test runners/dependencies may be managed per skill (Picbook owns a self-managed environment). Read the changed skill’s `SKILL.md` before assuming a global dependency setup.

## Installation and local diagnosis

- Preview discovered skills and destination state: `./install.sh --list`
- Preview changes without linking: `./install.sh --dry-run`
- Link to default Codex/Claude roots: `./install.sh`
- Use `--cleanup` only to remove stale managed symlinks that still point into this checkout; it deliberately does not delete ordinary directories or foreign links.
- Exercise Claude plugin discovery locally with `claude --plugin-dir .`.

For service-backed workflows, prefer their `--dry-run` and `--json` paths before an actual API or `rclone` operation. `rclone`, `yt-dlp`, `ffmpeg`, provider APIs, NotebookLM, Telegram, X, and WeChat are integrations—not test prerequisites for basic repository validation.

## Change playbooks

### Add a skill

1. Create `skills/guige-<name>/SKILL.md` with matching `name`/description frontmatter.
2. Add scripts/references/assets only when they support the contract; keep related files inside the skill.
3. Use a documented existing CLI for cross-skill services (image generation/upload), or design a new explicit CLI—not a private import.
4. Add focused tests for deterministic code.
5. Run the structural validator and update the README catalog when user-facing discovery changes.

### Change a plugin release

1. Update name/version in all applicable manifests together (see [Architecture](architecture/overview.md)).
2. Run `python3 scripts/validate.py`.
3. Inspect `git diff` to ensure the three distribution surfaces remain intentional.

### Change an external integration

1. Preserve consent, authorization, and opt-in upload/publish semantics.
2. Use redacted/local configuration only; never add a real `.env`, cookie, token, or test credential.
3. Keep local outputs/provenance on remote failures.
4. Test parser/payload/path logic locally and use dry-run/JSON behavior before live calls.

## Recent evolution that informs maintenance

The recent commit history shows the repository moving toward reusable, guarded workflow infrastructure rather than isolated prompts:

- **Validation and CI:** `1ca80b9` added the structural validator and GitHub Action, making manifest/skill consistency a hard quality gate.
- **Reusable delivery:** `f2c1ef5` added the root comic downloader/uploader, while the Drive skill and later `--layout task` support establish a more reusable delivery convention. Keep the root script’s special PDF/cache lifecycle separate from the generic uploader.
- **Picbook scale:** `ac04224` expanded Picbook to 30 pages, monthly archives, and tests; subsequent commits adjusted its default illustration aspect ratio. Treat defaults as deliberate product choices backed by code/tests.
- **Visual style iteration:** recent commits added a chubby-sketch hand-write option and adapted blog image prompt styles. Style guides and templates are active product behavior, not cosmetic leftovers.
- **Documentation/distribution:** the current HEAD `08bc0b8` added `AGENTS.md` compatibility; `CLAUDE.md` contains an uncommitted OpenWiki pointer at this run. Review such working-tree documentation changes separately from source behavior.

## OpenWiki maintenance

The untracked `.github/workflows/openwiki-update.yml` present during this run schedules a daily OpenWiki update and opens a PR containing `openwiki`, agent guidance, and the workflow itself. It was not part of the inspected committed baseline, so treat it as a proposed operational change until reviewed and committed. Generated documentation belongs under `openwiki/`; do not hand-edit the repository instruction brief `openwiki/INSTRUCTIONS.md` during routine documentation maintenance.
