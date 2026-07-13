# Architecture overview

## System shape

This is not one runtime application. It is a **plugin-distributed collection of independently owned skill contracts**. Every immediate `skills/guige-*` directory must contain `SKILL.md`; that document defines triggers, workflow, configuration, outputs, safety behavior, and change-specific validation. Implementations live only where a skill needs them.

```text
Claude Code / Codex / Anthropic Code
             │
     platform manifests
             │
         ./skills/
 ┌───────────┼──────────────────────┐
 visual foundations          source/publishing services
 imagen · drive-upload       X → Markdown · video · WeChat
 └───────────┴──────────────────────┘
             │
  task-scoped local materials + optional external delivery
```

## Distribution and identity

| Client surface | File | Role |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | Declares plugin identity and `skills: "./skills/"` |
| Claude marketplace | `.claude-plugin/marketplace.json` | Advertises GitHub marketplace source |
| Codex | `.codex-plugin/plugin.json` | Declares the same skill tree and Codex UI metadata/capabilities |
| Anthropic Code | `.agents/plugins/marketplace.json` | Installs the Git source at `main` under an availability-on-install policy |

`CLAUDE.md` requires the shared plugin name in the Claude/Codex/Agents manifests and version synchronization across Claude plugin, Codex plugin, and Claude marketplace metadata. `scripts/validate.py` enforces those structural checks. The Agents marketplace intentionally has no version field and tracks a mutable `main` ref, so release pinning is not supplied there.

## Core contracts and composition

- **`guige-imagen`** is the common image-generation foundation. It prefers its Python provider backend for repeatable automation; when no scoped provider configuration exists, it can delegate to the interactive runtime’s native image capability. It writes images under `~/Downloads/guige-skill-imagen/`. See `skills/guige-imagen/SKILL.md`.
- **`guige-drive-upload`** is the common delivery interface. It shells out to `rclone`, defaults to `gdrive:guige-skills/{skill-name}/{task-folder}/`, and runs only when explicitly requested, `--upload` is present, or `GUIGE_DRIVE_UPLOAD=1`. Callers retain local materials if delivery fails. See `skills/guige-drive-upload/SKILL.md`.
- Higher-level skills own their prompts, assets, work directories, and external integrations. For example, `guige-x-to-blog` composes X conversion, blog writing, local WebP conversion, and optional WeChat publication through named interfaces rather than source imports.

This composition rule is explicit in `CLAUDE.md`: use relative paths or `${CLAUDE_PLUGIN_ROOT}`, do not hard-code absolute user paths in reusable skills, and do not couple to other skills’ private directories.

## Runtime boundaries

| Boundary | Repository rule / evidence |
|---|---|
| Configuration and secrets | `.env` and `.guige-skills/` are ignored. `guige-imagen` scopes provider configuration to its own config locations and does not automatically consume ambient provider keys unless explicitly enabled. |
| Generated material | `.gitignore` excludes visual, slide, conversion, download, and WeChat artifact directories. Source, references, tests, and checked-in assets remain tracked. |
| Installation | `install.sh` discovers valid immediate skill directories and creates managed symlinks under Codex and Claude skill roots. It preserves a blocking non-symlink and can clean only stale links pointing into this checkout. |
| Claude session behavior | `hooks/hooks.json` has one `SessionStart` command, `hooks/session-start.sh`, that prints a skill quick reference. It does not mutate workspace state. |

## How to change architecture safely

1. Add or rename a skill only as a self-contained `skills/guige-*/SKILL.md` contract with matching frontmatter name.
2. If adding a shared capability, expose an explicit CLI and document its input/output/error behavior; do not create private cross-skill imports.
3. Update all required manifests together when plugin identity/version changes.
4. Preserve local-output-first behavior for services that can fail or require user authorization.
5. Run `python3 scripts/validate.py`, then the changed skill’s tests.

For concrete workflow topology, continue to [Content production](../workflows/content-production.md) and [Publishing and ingestion](../workflows/publishing-and-ingestion.md).