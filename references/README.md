# Shared References

Placeholder for cross-skill shared reference content.

**Currently empty.** Each skill keeps its own references inside `skills/<name>/references/`.

## When to add a file here

Add a file to this directory only when two or more skills genuinely share the **same** content. Examples:

- 品牌色与字体规范（`brand-palette.md`）
- 通用图片质量检查清单（`image-quality-checklist.md`）
- 通用 prompt 工程模板（`prompt-engineering-base.md`）

If only one skill uses a file, keep it inside that skill — do not pre-extract.

## Conventions

- One file per topic, kebab-case: `brand-palette.md`, `quality-checklist.md`
- Skills reference these via relative path: `../../references/<name>.md`
- Update the relevant skills` SKILL.md to point at the top-level file when moving content here
- Keep this README updated as files are added
