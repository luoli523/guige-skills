---
name: guige-x-to-blog
description: "将 X 推文下载、整理并改写为中文博客文章，复用原图并按既有博客发布流程交付。触发词：/x-to-blog、x 推文转博客、tweet to blog。"
version: 0.2.0
---

# X 推文转博客文章

一键将 X 推文转为中文博客文章，并发布到 `luoli523.github.io`。

## 语言

**固定中文**：文章内容、标题、描述、标签全部使用中文。与用户的交流语言跟随用户。

## 本项目闭环依赖

本 skill 已完全迁移到 `guige-skills` 仓库内闭环，不再依赖外部个人 skill 仓库或旧版第三方转换/发布 skill。

| 环节 | 使用本项目 skill / 工具 | 说明 |
|---|---|---|
| 下载 X 推文与媒体 | `guige-x-2-md` | `python3 skills/guige-x-2-md/scripts/main.py ... --download-media --json` |
| 写博客文章 | `guige-blog-post` | 使用本仓库托管的博客写作规范 |
| 图片转 WebP | `cwebp` 或 macOS `sips` | 本地工具，优先 `cwebp -q 80`，失败时 fallback |
| 发布微信公众号 | `guige-to-wechat` | `python3 skills/guige-to-wechat/scripts/main.py ...` |

## 输入

```text
/x-to-blog <tweet_url>
```

- `<tweet_url>`：X 推文或 X Article 链接，例如 `https://x.com/user/status/123456` 或 `https://x.com/i/article/123456`。

## 工作流总览

```text
X-to-Blog Progress:
- [ ] Phase 1: 下载推文（guige-x-2-md）
- [ ] Phase 2: 创建博客文章（guige-blog-post）
- [ ] Phase 3: 复用原文图片
- [ ] Phase 4: 等待用户提供 cover 图
- [ ] Phase 5: 验证、提交、推送
- [ ] Phase 6: 发布微信公众号（可选，guige-to-wechat）
```

---

## Phase 1: 下载推文

使用本仓库内的 `guige-x-2-md` 下载推文内容和媒体。

1. 按照 `guige-x-2-md` 的 Safety Gate 处理授权。该脚本会检查并执行 reverse-engineered X API consent gate。
2. 如果用户明确授权或本地已接受风险，可使用 `--accept-risk` 非交互执行。
3. 使用 `--download-media` 下载全部图片/视频，并使用 `--json` 取得机器可读路径。

推荐命令：

```bash
python3 skills/guige-x-2-md/scripts/main.py "<tweet_url>" \
  --download-media \
  --json \
  --accept-risk
```

记录 JSON 输出里的关键路径：

- Markdown 文件路径：`markdownPath`
- 图片目录路径：通常为 Markdown 同级的 `imgs/`
- 视频目录路径：通常为 Markdown 同级的 `videos/`

默认输出路径：

```text
x-to-markdown/{username-or-id}/{tweet-or-article-id}/{content-slug}.md
```

**失败处理**：

- 如果缺少登录态，引导用户设置 `X_AUTH_TOKEN` 和 `X_CT0`，或运行：

```bash
python3 skills/guige-x-2-md/scripts/main.py --login
```

- 如果 X Web API 变化导致失败，保留完整错误文本，让用户决定是否手动提供内容。

---

## Phase 2: 创建博客文章

读取下载好的推文 Markdown，然后按照本仓库 `guige-blog-post` 的规范写文章。

### 2.1 读取原文

1. 读取 Phase 1 下载的 Markdown 文件，提取正文、作者信息、原始链接和所有图片引用。
2. 统计原文中的图片数量和出现位置。
3. 若 Markdown front matter 中有 `sourceUrl`、`requestedUrl`、`authorName`、`tweetCount`、`coverImage` 等字段，优先保留为写作参考。

### 2.2 生成 slug

从推文主题生成 kebab-case slug，2-4 个英文单词，例如：

- Claude Code 相关 -> `claude-code-session-management`
- AI Agent 相关 -> `ai-agent-workflow`

### 2.3 创建目录和写文章

按照 `guige-blog-post` 的 Step 2-3 规范：

1. 创建博客目录：

```bash
mkdir -p /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>
```

2. 写入文章：

```text
/Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/index.md
```

Frontmatter：

```yaml
---
title: "中文标题"
description: "中文摘要，120 字以内"
date: YYYY-MM-DD
slug: <slug>
image: cover.webp
categories:
    - <类别>
tags:
    - tag1
    - tag2
    - tag3
---
```

文章要求：

- **语言**：全文中文。
- **结构**：必须遵守「钩子 -> 认知增量 -> Takeaway」三层结构。
- **章节顺序**：紧跟原文结构，不自行重排原文主线。
- **图片**：按原文图片出现顺序，在文章对应位置引用全部图片，不遗漏任何一张。
- **个人视角**：在翻译/整理原文的基础上，适当加入作者自己的使用体感和观点。
- **排版**：口语化但有技术深度，大量使用加粗，用表格对比概念。
- **参考资料**：文末附原推文或 X Article 链接。

反模式：

- 纯翻译/摘要，没有自己的观点。
- 自行调整原文章节顺序。
- 遗漏原文中的图片。
- 开头写“本文将介绍...”。
- 结尾写“以上就是全部内容”。

---

## Phase 3: 复用原文图片

将 `guige-x-2-md` 下载的全部图片复制到博客文章目录，并转换为 WebP 格式。

1. **复制并重命名**：从 Phase 1 的 `imgs/` 目录复制图片到 `content/post/<slug>/`，使用语义化文件名，例如 `context-rot.webp`、`rewind-flow.webp`。
2. **转换格式**：优先使用 `cwebp -q 80` 转 WebP；如果 `cwebp` 不可用，使用 macOS `sips -s format webp`。
3. **删除原始文件**：仅在确认 WebP 文件存在且可读后，删除博客文章目录内临时复制的 JPG/PNG 文件。不要删除 `x-to-markdown/.../imgs/` 下的原始下载文件。
4. **验证数量**：文章中引用的正文图片数量应等于原文图片数量，不含 `cover.webp`。

示例命令：

```bash
cwebp -q 80 input.png -o output.webp
sips -s format webp input.png --out output.webp
```

---

## Phase 4: 等待用户提供 cover 图

1. 在文章目录下创建 `image-prompts.md`，只包含 cover 图生成 prompt。
2. 使用 `skills/guige-blog-post/references/style-guide.md` 的深色技术风格：
   - 背景：`#07090f` 或 `#0d1117`
   - 主色：teal `#2dd4bf`
   - 辅色：amber `#f59e0b`
   - 16:9
   - 封面无文字

告知用户：

```text
文章和配图已就绪：
- 文章：content/post/<slug>/index.md
- 原文图片：已全部转换为 WebP（共 N 张）
- 只需生成 1 张封面图，prompt 在 image-prompts.md 中

请生成 cover 图，保存到同目录（PNG 或 WebP 均可）。完成后告诉我。
```

**停止在这里等待用户确认**。不要自行继续提交和发布。

---

## Phase 5: 验证、提交、推送

用户确认 cover 图就绪后：

1. 如果 cover 是 PNG/JPG，转换为 `cover.webp`。
2. 验证：
   - Frontmatter 完整：`title`、`description`、`date`、`slug`、`image`、`categories`、`tags`。
   - 所有图片引用都有对应 `.webp` 文件。
   - `cover.webp` 存在。
3. 可选预览：

```bash
cd /Users/luoli/dev/git/luoli523.github.io
hugo server -D
```

4. 提交推送：

```bash
cd /Users/luoli/dev/git/luoli523.github.io
git add content/post/<slug>/
git commit -m "feat: 新增 <文章标题简述> 文章，含 N 张配图"
git push origin master
```

如果 push 被拒绝，先 `git pull --rebase`，解决冲突后再 push。不要丢弃用户已有改动。

---

## Phase 6: 发布微信公众号（可选）

提交推送后，询问用户：

```text
需要同步发布到微信公众号吗？
```

如果用户确认：

1. 转换封面：

```bash
sips -s format jpeg cover.webp --out cover-wechat.jpg
```

2. 使用本仓库内的 `guige-to-wechat`：

```bash
python3 /Users/luoli/dev/git/guige-skills/skills/guige-to-wechat/scripts/main.py \
  /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/index.md \
  --theme simple \
  --author 鬼哥 \
  --cover /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/cover-wechat.jpg
```

3. `cover-wechat.jpg` 只是微信公众号 API 临时封面，不要 commit 到博客仓库。

---

## 错误恢复

| 场景 | 处理 |
|---|---|
| 推文下载失败（认证） | 引导用户设置 `X_AUTH_TOKEN` 和 `X_CT0`，或运行 `python3 skills/guige-x-2-md/scripts/main.py --login` |
| 推文下载超时 | 重试一次，仍失败则让用户手动提供内容 |
| 图片转换失败（cwebp） | fallback 到 `sips -s format webp` |
| cover 未提供 | 停止在 Phase 4，等待用户生成封面 |
| git push 被拒绝 | `git pull --rebase` 后重试 |
| 微信 API 凭据缺失 | 按 `guige-to-wechat` 说明配置 `WECHAT_APP_ID` / `WECHAT_APP_SECRET` 或 `~/.guige-skills/.env` |

## 闭环自检

迁移后，`guige-x-to-blog` 应只依赖本项目内 skill：

- `skills/guige-x-2-md`
- `skills/guige-blog-post`
- `skills/guige-to-wechat`
