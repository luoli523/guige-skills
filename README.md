# Gui Ge Skills

鬼哥个人 Skills 仓库，用来集中维护可复用的本地 AI 工作流。

## 目录结构

```text
.
├── install.sh
├── README.md
└── skills/
    ├── guige-blog-post/
    │   ├── SKILL.md
    │   └── references/
    ├── guige-drive-upload/
    │   ├── SKILL.md
    │   └── scripts/
    ├── guige-disassembly-diagram/
    │   ├── SKILL.md
    │   ├── agents/
    │   └── references/
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
    ├── guige-slides/
    │   ├── SKILL.md
    │   ├── agents/
    │   ├── references/
    │   └── scripts/
    ├── guige-to-wechat/
    │   ├── SKILL.md
    │   └── scripts/
    ├── guige-video-download/
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/
    ├── guige-x-2-md/
    │   ├── SKILL.md
    │   └── scripts/
    ├── guige-x-to-blog/
    │   └── SKILL.md
    └── guige-svg/
        ├── SKILL.md
        ├── agents/
        ├── references/
        └── scripts/
```

每个 skill 都放在 `skills/<skill-name>/` 下，并包含必需的 `SKILL.md`。资源文件、参考文档和辅助脚本分别放在该 skill 自己的 `assets/`、`references/` 和 `scripts/` 目录中。

## 当前 Skill

- `guige-blog-post`：写作并发布文章到 `luoli523.github.io` Hugo 博客，覆盖选题/研究、文章结构、配图 prompt、图片转 WebP、Hugo 预览、提交推送，以及可选微信公众号同步。
- `guige-drive-upload`：通用 Google Drive 上传后端，通过 `rclone` 把各 skill 生成的 materials 上传到 `guige-skills/<skill-name>/<task-folder>/`。
- `guige-disassembly-diagram`：生成中文拆解图、爆炸图、剖面图和产品结构科普知识卡片，覆盖整体外观、内部结构、关键部件、材质标注和工作原理流程图，复用 `guige-imagen` 生图底座，并可按需上传到 Google Drive。
- `guige-imagen`：鬼哥 skill set 的图片生成底座，支持 runtime 图片工具 fallback 和 OpenAI/Google Python API 后端，最终图片统一放到 `~/Downloads/guige-skill-imagen/`。
- `guige-infographic`：生成鬼哥风格信息图，内置鬼哥角色图，支持 `--layout`、`--style`、`--aspect`、`--lang` 参数，并可按需通过 `guige-drive-upload` 上传到 Google Drive。
- `guige-hand-write-pic`：生成一页式手绘教育信息图，固定暖米色纸张、sketchnote、粉彩卡片和短标签风格；复用 `guige-imagen` 生图底座，并可按需通过 `guige-drive-upload` 上传到 Google Drive。
- `guige-slides`：把文章、主题或素材整理成适合阅读和分享的图片式幻灯片，生成 outline、逐页 prompt、PNG slide，并用 Python 标准库脚本合并为 PPTX/PDF，可按需上传到 Google Drive。
- `guige-svg`：生成可编辑 SVG 图表和时间表，使用结构化 JSON spec 与 Python 确定性渲染器，支持矩阵、流程图、时间线和架构图，可按需导出 PNG 并上传到 Google Drive。
- `guige-to-wechat`：将 Markdown、HTML 或纯文本发布到微信公众号草稿箱，Python 标准库实现官方 API 路径，支持 front matter、微信友好 HTML、正文图片上传、封面素材上传、草稿创建和 dry-run。
- `guige-video-download`：使用自包含的 Gui Ge 工作流封装 `yt-dlp`，下载 YouTube、YouTube Shorts、X.com 和 Twitter 视频，支持视频、音频、封面、字幕、metadata、JSON 输出和可选 Google Drive 上传。
- `guige-x-2-md`：将 X/Twitter 推文、线程和 X Articles 转为 Markdown，使用 Python 标准库实现逆向 X Web API 客户端，支持登录 cookie、YAML front matter、媒体本地化和 JSON 输出。
- `guige-x-to-blog`：将 X 推文或 X Article 下载为 Markdown、复用原图整理成中文 Hugo 博客文章，并按本项目内 `guige-x-2-md`、`guige-blog-post`、`guige-to-wechat` 形成闭环工作流。

## `guige-disassembly-diagram` 快速使用

`guige-disassembly-diagram` 用来生成中文教学拆解图、爆炸图、剖面图和产品结构知识卡片。默认输出 `hybrid + landscape + zh`，会把主题整理成整体外观、内部结构、关键部件、材质特征和工作原理流程图，再交给 `guige-imagen` 或当前 runtime 的图片生成工具出图。

```text
/guige-disassembly-diagram 生成一张关于空气炸锅的中文拆解图 --no-confirm
/guige-disassembly-diagram cybertruck --mode hybrid --aspect landscape --no-confirm --upload
/guige-disassembly-diagram 机械键盘 --mode exploded --aspect 4:3
```

常用参数：

- `--mode hybrid|exploded|cutaway|auto`：控制拆解图重点，默认 `hybrid`。
- `--aspect landscape|portrait|square|4:3|自定义比例`：控制画幅，默认 `landscape`。
- `--lang zh|en|...`：控制图中文字语言，默认简体中文。
- `--upload`：生成后通过 `guige-drive-upload` 上传到 Google Drive。
- `--no-confirm`：跳过参数确认，直接生成。

## `guige-to-wechat` 快速使用

`guige-to-wechat` 是 `baoyu-post-to-wechat` 的 Python API 路径重写版，聚焦微信公众号官方接口发草稿；原版的 Chrome CDP 浏览器自动化和图文贴图发布没有移植到这个版本。

凭据优先读取 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`，也可以放到 `.guige-skills/.env`、`~/.guige-skills/.env`，或 `.guige-skills/guige-to-wechat/EXTEND.md` 的账号配置里。兼容读取已有的 `baoyu-post-to-wechat` 配置。

不要把真实公众号凭据提交到仓库；个人机器上建议放在 `~/.guige-skills/.env`，并设置为仅当前用户可读写。

```bash
# 渲染并校验，不调用微信接口
python3 skills/guige-to-wechat/scripts/main.py article.md --cover cover.jpg --dry-run --json

# 发布 Markdown 到公众号草稿箱
python3 skills/guige-to-wechat/scripts/main.py article.md --cover cover.jpg

# 指定账号和样式
python3 skills/guige-to-wechat/scripts/main.py article.md --account guige --theme simple --color teal --cover cover.jpg

# HTML 或纯文本输入
python3 skills/guige-to-wechat/scripts/main.py article.html --title "标题" --summary "摘要" --cover cover.jpg
python3 skills/guige-to-wechat/scripts/main.py "一段要发布到公众号的内容" --title "标题" --cover cover.jpg
```

常用 front matter：

```yaml
---
title: "文章标题"
description: "摘要"
author: "鬼哥"
image: cover.webp
---
```

## `guige-x-2-md` 快速使用

`guige-x-2-md` 使用逆向的 X Web API，不是官方 API。首次运行会要求确认风险，并需要可用的 X 登录 cookie。优先读取环境变量 `X_AUTH_TOKEN` 和 `X_CT0`；如果没有 cookie，可先运行 `--login` 通过 Chrome/Edge 刷新本地缓存。

```bash
# 转换推文或线程
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890

# 转换并下载图片/视频到 Markdown 旁边的 imgs/、videos/
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 --download-media

# 转换 X Article
python3 skills/guige-x-2-md/scripts/main.py https://x.com/i/article/1234567890

# 输出 JSON，便于 agent 获取 markdownPath/imageDir/videoDir
python3 skills/guige-x-2-md/scripts/main.py https://x.com/username/status/1234567890 --json

# 刷新登录 cookie
python3 skills/guige-x-2-md/scripts/main.py --login
```

默认输出路径：

```text
x-to-markdown/{username-or-id}/{tweet-or-article-id}/{content-slug}.md
```

## `guige-video-download` 快速使用

`guige-video-download` 用来下载 YouTube、YouTube Shorts、X.com 和 Twitter 视频素材。它使用 `yt-dlp` 作为下载引擎，默认下载 best MP4、封面和 metadata，并把结果保存到 `~/Downloads/guige-skill-video/`。`ffmpeg` 用于高质量音视频合并和音频格式转换。

安全边界：只用于用户有权访问和保存的公开视频、自己的内容或已获授权内容；不要用于绕过 DRM、付费墙、私有账号权限或平台访问限制。`--cookies-from-browser` 只用于用户本人浏览器里已经能正常访问的内容。

```bash
# 默认下载：best MP4 + 封面 + metadata
python3 skills/guige-video-download/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --json

# 下载 X/Twitter 视频
python3 skills/guige-video-download/scripts/main.py 'https://x.com/user/status/1234567890' --json

# 指定清晰度上限
python3 skills/guige-video-download/scripts/main.py 'https://youtu.be/VIDEO_ID' --quality 1080p --json

# 只下载音频
python3 skills/guige-video-download/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --audio-only --audio-format mp3 --json

# 下载字幕
python3 skills/guige-video-download/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --subtitles --languages zh,en --json

# 使用浏览器 cookies 下载用户本人可访问的内容
python3 skills/guige-video-download/scripts/main.py 'https://x.com/user/status/1234567890' --cookies-from-browser chrome --json

# 下载后上传整个输出目录到 Google Drive
python3 skills/guige-video-download/scripts/main.py 'https://www.youtube.com/watch?v=VIDEO_ID' --upload --json
```

默认输出路径：

```text
~/Downloads/guige-skill-video/{platform}/{author-or-channel}/{title-or-id}/
```

常见输出文件：

- `video.mp4`：最终视频文件。
- `audio.mp3` / `audio.m4a`：音频模式输出。
- `video.jpg` / `video.webp`：封面图。
- `video.info.json`：`yt-dlp` metadata。
- `source-url.txt`：原始 URL。
- `download-result.json`：Gui Ge 下载结果摘要，便于 agent 读取路径和上传信息。

## `guige-slides` 快速使用

`guige-slides` 用来把内容转成图片式幻灯片：先生成 `analysis.md` 和 `outline.md`，再为每页写入 `prompts/NN-slide-*.md`，然后逐页生成为 PNG，最后合并为 PPTX/PDF。PPTX 每页是一张完整图片，适合分享和阅读，不是可逐字编辑的普通 PPT 排版。

```text
/guige-slides 把这篇文章做成 12 页中文幻灯片 --style blueprint --no-confirm
/guige-slides 生成一套给高管看的 AI agent 趋势简报 --audience executives --slides 10 --upload
/guige-slides 根据 slide-deck/my-topic/prompts 重新生成第 3 页 --regenerate 3
```

常用参数：

- `--style blueprint|sketch-notes|hand-drawn-edu|notion|minimal|corporate|...`：控制视觉预设。
- `--audience general|beginners|experts|executives`：控制信息密度和表达方式。
- `--slides N`：目标页数，建议 5-25 页。
- `--outline-only`：只生成大纲。
- `--prompts-only`：只生成逐页生图 prompt。
- `--images-only`：用已有 prompts 生成图片。
- `--regenerate 3`：重新生成某一页或若干页。
- `--upload`：生成后通过 `guige-drive-upload` 上传整个 deck 文件夹。

合并脚本：

```bash
python3 skills/guige-slides/scripts/merge_to_pptx.py slide-deck/{topic-slug}
python3 skills/guige-slides/scripts/merge_to_pdf.py slide-deck/{topic-slug}
```

默认输出结构：

```text
slide-deck/{topic-slug}/
├── outline.md
├── prompts/
├── 01-slide-cover.png
├── NN-slide-{slug}.png
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

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
