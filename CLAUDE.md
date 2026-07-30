# guige-skills

鬼哥个人 Skills 仓库，集中维护可复用的本地 AI 工作流。同时支持 Claude Code / Codex / Anthropic Code 三套 plugin 分发机制。

## Project Structure

```
.claude-plugin/         → Claude Code plugin manifest + marketplace 声明
.codex-plugin/          → Codex 专属 plugin 配置
.agents/plugins/        → Anthropic Code marketplace 声明
hooks/                  → Claude Code 生命周期钩子（SessionStart 输出 skill 速查）
references/             → 跨 skill 共享参考资料（当前为占位，按需启用）
skills/<skill-name>/    → 每个 skill 一个子目录，必含 SKILL.md
  ├── SKILL.md          → 必需，frontmatter 含 name + description
  ├── references/       → skill 私有参考资料
  ├── scripts/          → skill 私有脚本（Python/Bash）
  ├── assets/           → skill 私有静态资源
  └── agents/           → Codex 风格的子 agent（YAML 格式）
install.sh              → 本地软链接安装兼容脚本
README.md               → 用户文档
```

## Conventions

- 每个 skill 在 `skills/<name>/SKILL.md`，frontmatter 至少含 `name` 与 `description`
- skill 名一律 `guige-` 前缀，kebab-case
- 三套 plugin 配置的 `name` 必须同步：`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json` 顶层 `name`；`.agents/plugins/marketplace.json` 的 `plugins[0].name`（全部应为 `guige`）
- 版本号 `version` 在两份 `plugin.json` 与 `.claude-plugin/marketplace.json` 的 `metadata.version` 之间同步（`.agents` schema 无 version 字段，不参与）
- 各 manifest 的 `description` 允许按平台调整文案，不强制同步
- 路径引用使用相对路径或 `${CLAUDE_PLUGIN_ROOT}`，禁止硬编码绝对路径
- skill 间不复制粘贴内容；共享资源放顶层 `references/`（如果有）
- skill 间通过明确 CLI 接口调用（如 `guige-drive-upload`），不读对方私有目录

## Runtime Output Directories

下列目录是 skill 的运行时输出，在 `.gitignore` 中，**禁止删除或污染**：

- `infographic/`、`hand-write-pic/`、`imagen/`、`svg/`、`slide-deck/`
- `x-to-markdown/`、`post-to-wechat/`、`wechat/`
- `downloads/`、`generated/`、`digital-human/`
- `~/Downloads/guige-skill-imagen/`、`~/Downloads/guige-skill-video/`

## Boundaries

- Always: 修改任一 plugin manifest 时，同步更新另外两套
- Always: skill 之间通过明确的 CLI 接口调用
- Never: 在 skill 内部硬编码用户目录或绝对路径
- Never: 让 `guige-*` skill 依赖 `baoyu-*` skill 的配置或脚本
- Never: 误删 `Runtime Output Directories` 中列出的目录

## Commands

- 本地测试：`claude --plugin-dir .`
- 安装到本机：`./install.sh`（软链接到 `~/.claude/skills` 和 `~/.codex/skills`）
- 公开分发：通过 GitHub `luoli523/guige-skills` marketplace

<!-- OPENWIKI:START -->

## OpenWiki

This repository uses OpenWiki for recurring code documentation. Start with `openwiki/quickstart.md`, then follow its links to architecture, workflows, domain concepts, operations, integrations, testing guidance, and source maps.

Refresh the repository wiki locally with OpenWiki when needed. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->
