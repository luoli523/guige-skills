# Gui Ge Skills: Quickstart

`guige-skills` is a multi-platform collection of **13 local AI workflow skills**. It packages visual and written content creation, source acquisition, publishing, and optional delivery for Claude Code, Codex, and Anthropic Code. This wiki is an engineering map—not a replacement for a skill’s user-facing `SKILL.md` contract.

## Start here

1. Find the relevant workflow family below and read the owning `SKILL.md` before changing or running it.
2. Follow the repository invariants in [Architecture overview](architecture/overview.md), especially synchronized manifests, relative paths, and explicit CLI boundaries.
3. Use [Engineering guide](engineering.md) for installation, configuration boundaries, validation, and tests. The baseline structural gate is `python3 scripts/validate.py`.
4. Keep ignored runtime output out of Git; `.gitignore` excludes working directories such as `infographic/`, `slide-deck/`, `x-to-markdown/`, and `*.wechat.html`.

## Navigate by task

| Area | Primary skills | Go next |
|---|---|---|
| Visual and authored content | Imagen, infographic, hand-write cards, disassembly diagrams, slides, SVG, picbooks, blog posts | [Content production workflows](workflows/content-production.md) |
| Acquisition, delivery, and publishing | X-to-Markdown, video download, Drive upload, WeChat drafts, X-to-blog | [Publishing and ingestion workflows](workflows/publishing-and-ingestion.md) |
| Plugin/runtime design | Three distribution manifests, lifecycle hook, skill contract, shared services | [Architecture overview](architecture/overview.md) |
| Maintenance | Source map, validation, tests, installation, CI, history, change checklists | [Engineering guide](engineering.md) |

## Repository model

- A skill is `skills/<skill-name>/` with a required YAML-frontmatter `SKILL.md`; it can own `scripts/`, `references/`, `assets/`, and optional `agents/` metadata.
- Names use the `guige-` prefix. Skills are independently installable and must communicate through documented CLIs, not another skill’s private files.
- `guige-imagen` is the shared raster-image foundation. `guige-drive-upload` is the reusable, opt-in Drive delivery backend. Higher-level skills create their own materials and may invoke those interfaces.
- Root `scripts/validate.py` checks frontmatter identity, cross-platform manifest synchronization, Claude’s declared skill path, and selected shell executable bits.

## Safe first checks

```bash
# Structural repository contract
python3 scripts/validate.py

# Show skill-installation effects without writing links
./install.sh --dry-run --list

# Local Claude plugin development
claude --plugin-dir .
```

Run the narrow test suite for an edited skill in addition to validation; see the [focused test map](engineering.md#focused-test-map).

## Boundaries to preserve

- Never commit or inspect live `.env` or `.guige-skills/` configuration. They are ignored machine-local configuration/secrets.
- Do not delete or treat generated folders as source. They are intentionally ignored runtime artifacts.
- Do not turn optional delivery into implicit delivery: uploads and publication are normally user-requested or explicitly enabled.
- The docs use the committed source baseline `08bc0b8` plus clearly labeled working-tree evidence. The OpenWiki scheduler currently exists as an **untracked** workflow and becomes repository behavior only after review and commit.

## Canonical sources

- User-facing overview and examples: [`README.md`](../README.md)
- Contribution/runtime rules: [`CLAUDE.md`](../CLAUDE.md) (also exposed as `AGENTS.md`)
- Skill behavior contracts: [`skills/*/SKILL.md`](../skills/)
- Structural validator: [`scripts/validate.py`](../scripts/validate.py)
