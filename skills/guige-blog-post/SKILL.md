---
name: guige-blog-post
description: "Write and publish blog posts to luoli523.github.io Hugo blog. Trigger on: /blog-post, writing blog post, publish post, write article for blog."
version: 0.1.0
---

# Blog Post Workflow

End-to-end workflow for writing, illustrating, and publishing blog posts to the Hugo blog at `luoli523.github.io`.

## Language

**Match user's language**: Respond in the same language the user uses.

## Blog Repository

**Repo path**: `/Users/luoli/dev/git/luoli523.github.io`
**Generator**: Hugo 0.158.0 extended, theme `hugo-theme-stack`
**Post path**: `content/post/<slug>/index.md`
**Post URL**: `https://luoli523.github.io/p/<slug>/`

## Workflow Overview

Copy this checklist and update as you progress:

```
Blog Post Progress:
- [ ] Step 0: Load preferences
- [ ] Step 1: Determine input and research
- [ ] Step 2: Create post structure
- [ ] Step 3: Write article
- [ ] Step 4: Generate image prompts
- [ ] Step 5: User generates images (manual, wait for user)
- [ ] Step 6: Convert images to WebP
- [ ] Step 7: Validate and preview
- [ ] Step 8: Commit and push
- [ ] Step 9: Publish to WeChat (optional)
```

---

### Step 0: Load Preferences

Read the blog repo's CLAUDE.md for project rules:

```bash
cat /Users/luoli/dev/git/luoli523.github.io/CLAUDE.md
```

**Defaults** (can be overridden by user):

| Setting | Default |
|---------|---------|
| Author | 鬼哥 |
| Category | AI |
| Image format | WebP |
| Cover filename | cover.webp |
| Design palette | Dark mode: `#07090f` bg, `#2dd4bf` teal accent |

### Step 1: Determine Input Type

| User Input | Action |
|------------|--------|
| A topic/idea (string) | Research the topic, then write article |
| A markdown file path | Use as article content, validate frontmatter |
| An existing post directory | Skip to Step 6 (image conversion) |
| `/blog-post` with no args | Ask user what they want to write about |

**If researching a topic**:

1. Use `Agent` with `subagent_type=general-purpose` for web research — gather facts, perspectives, data
2. Use `WebFetch` for specific URLs the user provides
3. Collect enough material before writing — quality research makes quality articles

**If user provides a URL or reference content**: Extract and summarize key points as source material.

### Step 2: Create Post Structure

1. **Generate slug**: kebab-case, 2-4 English words (e.g., `karpathy-llm-wiki`, `gemma4-analysis`)

2. **Create directory**:

```bash
mkdir -p /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>
```

3. **Verify no conflict**:

```bash
ls /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/
```

### Step 3: Write Article

**Frontmatter template** (YAML, between `---` delimiters):

```yaml
---
title: "标题：副标题格式"
description: "1-2 句话的 SEO 摘要，120 字以内。这句话本身就是一个钩子——抛出反常识/痛点/数字，而不是流水账概括。Hugo 首页和微信公众号摘要都会用到它，它是文章的'第二个钩子'。"
date: YYYY-MM-DD
slug: <slug>
image: cover.webp
categories:
    - <category>
tags:
    - tag1
    - tag2
    - tag3
---
```

**Category options and their announcement colors**:

| Category | Color | Type |
|----------|-------|------|
| AI | teal | note |
| LLM | teal | note |
| 工具 | amber | tool |
| Big Data | amber | tool |
| 随想 | purple | note |
| 生活 | red | life |

**文章骨架——三层结构（必须遵守，骨架比皮肤重要）**

每篇博客都要有这三层，缺一层就不是合格的文章：

**① 钩子（开头 1-3 句）—— 让人停下来**

- 划走只需要 0.3 秒，第一句决定生死
- 三选一：**反常识断言** / **痛点共鸣** / **无法忽略的数字**
- 反例（平庸）：「今天我们来聊一聊 X 这个话题」、「本文将介绍 X」
- 正例（有钩子）：
  - 「150 行代码就能造一个数字分身，但它只会聊天，不会做事」（数字 + 反转）
  - 「你以为你的推文没人看是因为算法？其实是因为你只在"写"，没在"设计"」（痛点 + 反常识）
  - 「我用这个方法三天涨了 3000 粉，但没人告诉你它有个致命缺点」（数字 + 钩子）

**② 认知增量（主体）—— 让人觉得值**

- 光吸引眼球没用，点进来是废话，下次不会再点
- 主体必须交付至少一样：**新视角** / **可复用方法** / **信息差**
- 写每个章节前问自己："读者从这段能带走什么？" 如果答不上来，这段就要删
- 规避"学术综述腔"：不做全景扫描，要做**有观点的取舍**

**③ Takeaway（结尾）—— 让人忍不住收藏/转发**

- 给一个明确的**行动指令**或**可复用的总结**
- 三种常见收尾：
  - **清单式总结**：「回顾一下，搭建 X 只需要做四件事：1... 2... 3... 4...」
  - **FOMO 式**：「这个方法我用了三个月，效果是 XX——收藏这条，下次写的时候直接套」
  - **挑战/留问**：「如果你也做了类似的项目，欢迎告诉我你的版本」

**自检清单**（写完对照一下）：
- [ ] 第一句能让人 3 秒内想继续读？
- [ ] 中间每个章节都有读者能带走的东西？
- [ ] 结尾给了明确的 takeaway 或行动？

**任何一层缺失 = 不发。**

---

**排版风格（形式）**：

- 口语化但有技术深度，偶尔幽默
- 大量使用 **加粗** 强调关键观点
- 用表格对比概念
- 用代码块展示技术细节
- 每个大章节之间用 `---` 分隔
- 图片引用格式：`![描述](filename.webp)`
- 文章末尾附参考资料链接

**反模式（写完自查是否中招）**：

- ❌ 开头"本文将介绍..."、"今天我们来聊..."（零钩子）
- ❌ 中间写成维基百科式的综述（没观点 = 没增量）
- ❌ 结尾"以上就是全部内容，谢谢阅读"（没 takeaway）
- ❌ 堆砌 ChatGPT 味的排比短句（"它不仅 X，还 Y，更重要的是 Z"）
- ❌ 每个小标题都工整对仗——读起来像目录，不像文章

**Image placement**: Plan 4-6 images at natural section breaks. For each image, note:
- Filename (kebab-case, `.webp` suffix)
- Position in article (after which section)
- What it should depict

Write the article to: `/Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/index.md`

### Step 4: Generate Image Prompts

Create `image-prompts.md` in the same post directory. This file serves as a specification for the user to generate images with AI tools.

**Template**:

```markdown
# 文章配图生成 Prompt

生成后将图片保存到本目录，格式为 .webp 或 .png（会自动转为 .webp），文件名与文章中引用一致。

---

## 1. cover.webp — 文章封面

{prompt}

---

## 2. <filename>.webp — <描述>

{prompt}

...

---

## 使用说明

1. 将上述 prompt 分别输入 AI 图片生成工具（如 Midjourney, DALL-E, Ideogram 等）
2. 建议使用 16:9 比例，分辨率至少 1920x1080
3. 生成后保存到本目录（PNG 或 WebP 均可，后续会统一转为 WebP）
4. 文章中已经用 `![描述](文件名.webp)` 格式引用了这些图片
```

**Image prompt style guide** (maintain visual consistency across posts):

- Background: deep dark navy `#07090f` or `#0d1117`
- Primary accent: teal `#2dd4bf`
- Secondary accent: amber `#f59e0b`
- Tertiary accents: purple `#a78bfa`, red `#f87171`
- Style keywords: "clean tech illustration", "dark mode aesthetic", "minimal and elegant"
- Aspect ratio: 16:9
- Always end with: "No text. 16:9 aspect ratio." (for cover) or specify text needs
- Match the blog's Ghost Protocol dark palette

### Step 5: Wait for User to Generate Images

**STOP HERE** and tell the user:

```
文章和配图 prompt 已就绪：
- 文章: content/post/<slug>/index.md
- 配图 prompt: content/post/<slug>/image-prompts.md

请根据 image-prompts.md 中的 prompt 生成图片，保存到同一目录下。
PNG 或 WebP 格式均可，我会统一转换。

生成完成后告诉我，我继续处理。
```

**Do NOT proceed until user confirms images are ready.**

### Step 6: Convert Images to WebP

1. **Check for non-WebP images**:

```bash
ls /Users/luoli/dev/git/luoli523.github.io/content/post/<slug>/*.{png,jpg,jpeg} 2>/dev/null
```

2. **Convert using cwebp** (preferred) or sips (fallback):

```bash
# For each PNG/JPG file:
cwebp -q 80 <input>.png -o <output>.webp
# Fallback:
sips -s format webp <input>.png --out <output>.webp
```

3. **Delete original PNG/JPG files** after confirming WebP files exist.

4. **Verify all image references in article have matching files**:

```bash
# Extract image references from article
grep -oP '!\[.*?\]\(\K[^)]+' content/post/<slug>/index.md
# List actual image files
ls content/post/<slug>/*.webp
```

### Step 7: Validate and Preview

1. **Check frontmatter completeness**: title, description, date, slug, image, categories, tags
2. **Check all images referenced in article exist as .webp files**
3. **Check cover.webp exists** (required for announcement system)
4. **Optionally run Hugo to verify**:

```bash
cd /Users/luoli/dev/git/luoli523.github.io && hugo server -D &
# Then user can preview at http://localhost:1313/p/<slug>/
```

### Step 8: Commit and Push

```bash
cd /Users/luoli/dev/git/luoli523.github.io

# Stage all post files (article + images + image-prompts.md)
git add content/post/<slug>/

# Commit
git commit -m "$(cat <<'EOF'
feat: 新增 <文章标题简述> 文章，含 N 张插图

- <1-2 句描述文章内容>
EOF
)"

# Push
git push origin master
```

**After push**: GitHub Actions will auto-update `data/announcements.yaml` with a new homepage announcement entry.

### Step 9: Publish to WeChat (Optional)

Ask the user: "需要同步发布到微信公众号吗？"

If yes, invoke the `/post-to-wechat` skill with the article:

**IMPORTANT**: WeChat API does not support WebP covers. Convert cover first:

```bash
sips -s format jpeg content/post/<slug>/cover.webp --out content/post/<slug>/cover-wechat.jpg
```

Then pass to the post-to-wechat skill. The skill handles the rest (theme, metadata, API upload).

Key parameters to forward:
- Input file: `content/post/<slug>/index.md`
- Cover: `content/post/<slug>/cover-wechat.jpg`
- Author: 鬼哥 (from EXTEND.md default)
- Theme: from EXTEND.md (default: simple)

---

## Quick Commands

| Command | Effect |
|---------|--------|
| `/blog-post <topic>` | Full workflow: research → write → images → publish |
| `/blog-post <file.md>` | Import existing markdown as blog post |
| `/blog-post --images <slug>` | Convert images for existing post |
| `/blog-post --publish <slug>` | Commit, push, and optionally WeChat publish |

## File Structure Reference

```
content/post/<slug>/
├── index.md              # Article (frontmatter + markdown)
├── image-prompts.md      # Image generation prompts
├── cover.webp            # Cover image (required)
├── *.webp                # Inline images
└── cover-wechat.jpg      # WeChat cover (generated on demand, do NOT commit)
```
