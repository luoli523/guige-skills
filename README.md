# Gui Ge Skills

鬼哥个人 Skills 仓库，用来集中维护可复用的本地 AI 工作流。

## 目录结构

```text
.
├── install.sh
├── README.md
└── skills/
    ├── guige-drive-upload/
    │   ├── SKILL.md
    │   └── scripts/
    ├── guige-imagen/
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/
    ├── guige-infographic/
    │   ├── SKILL.md
    │   ├── assets/
    │   ├── references/
    │   └── scripts/
    ├── guige-hand-write-pic/
    │   ├── SKILL.md
    │   └── references/
    └── guige-svg/
        ├── SKILL.md
        ├── agents/
        ├── references/
        └── scripts/
```

每个 skill 都放在 `skills/<skill-name>/` 下，并包含必需的 `SKILL.md`。资源文件、参考文档和辅助脚本分别放在该 skill 自己的 `assets/`、`references/` 和 `scripts/` 目录中。

## 当前 Skill

- `guige-drive-upload`：通用 Google Drive 上传后端，通过 `rclone` 把各 skill 生成的 materials 上传到 `guige-skills/<skill-name>/<task-folder>/`。
- `guige-imagen`：鬼哥 skill set 的图片生成底座，支持 runtime 图片工具 fallback 和 OpenAI/Google Python API 后端，最终图片统一放到 `~/Downloads/guige-skill-imagen/`。
- `guige-infographic`：生成鬼哥风格信息图，内置鬼哥角色图，支持 `--layout`、`--style`、`--aspect`、`--lang` 参数，并可按需通过 `guige-drive-upload` 上传到 Google Drive。
- `guige-hand-write-pic`：生成一页式手绘教育信息图，固定暖米色纸张、sketchnote、粉彩卡片和短标签风格；复用 `guige-imagen` 生图底座，并可按需通过 `guige-drive-upload` 上传到 Google Drive。
- `guige-svg`：生成可编辑 SVG 图表和时间表，使用结构化 JSON spec 与 Python 确定性渲染器，支持矩阵、流程图、时间线和架构图，可按需导出 PNG 并上传到 Google Drive。

## 本地初始化

执行安装脚本会扫描 `skills/*/SKILL.md`，并把有效 skill 以软链接方式安装到本机 skill 目录。

```bash
./install.sh
```

默认目标目录：

- `${CODEX_HOME:-~/.codex}/skills`
- `~/.claude/skills`

常用命令：

```bash
./install.sh --dry-run
./install.sh --list
./install.sh --cleanup
```

也可以指定安装目标：

```bash
./install.sh --target ~/.codex/skills
./install.sh --target ~/.claude/skills --target ~/.codex/skills
```

或使用环境变量指定多个目标目录：

```bash
GUIGE_SKILLS_TARGETS="$HOME/.codex/skills:$HOME/.claude/skills" ./install.sh
```

## 更新 Skill

修改或新增 skill 后重新运行：

```bash
./install.sh
```

如果删除了某个本地 skill，可以运行：

```bash
./install.sh --cleanup
```

`--cleanup` 只清理指向本仓库的失效软链接，不会删除真实的 skill 源目录。
