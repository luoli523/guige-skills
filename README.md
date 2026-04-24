# Gui Ge Skills

鬼哥个人 Skills 仓库，用来集中维护可复用的本地 AI 工作流。

## 目录结构

```text
.
├── install.sh
├── README.md
└── skills/
    └── guige-infographic/
        ├── SKILL.md
        ├── assets/
        ├── references/
        └── scripts/
```

每个 skill 都放在 `skills/<skill-name>/` 下，并包含必需的 `SKILL.md`。资源文件、参考文档和辅助脚本分别放在该 skill 自己的 `assets/`、`references/` 和 `scripts/` 目录中。

## 当前 Skill

- `guige-infographic`：生成鬼哥风格信息图，内置鬼哥角色图，支持 `--layout`、`--style`、`--aspect`、`--lang` 参数，并可按需上传到 Google Drive。

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
