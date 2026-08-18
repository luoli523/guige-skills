---
name: guige-blog-post
description: "Write distinctive, evidence-based, shareable blog posts in Guige's veteran AI/technology voice, then illustrate and publish them to the luoli523.github.io Hugo blog. Trigger on: /blog-post, writing blog post, publish post, write article for blog."
version: 0.3.0
---

# Blog Post Workflow

End-to-end workflow for writing, illustrating, and publishing blog posts to the Hugo blog at `luoli523.github.io`.

## Language

**Match user's language**: Respond in the same language the user uses.

## Blog Repository

Resolve the blog repository before doing any work. Use, in order:

1. A path explicitly provided by the user
2. The `BLOG_REPO` environment variable
3. A local sibling repository named `luoli523.github.io`

If none can be resolved, ask the user for the repository path. Never hardcode a user home directory in generated files or scripts.

**Generator**: Hugo 0.158.0 extended, theme `hugo-theme-stack`
**Post path**: `content/post/<slug>/index.md`
**Post URL**: `https://luoli523.github.io/p/<slug>/`

## Workflow Overview

Copy this checklist and update as you progress:

```
Blog Post Progress:
- [ ] Step 0: Load preferences
- [ ] Step 1: Define reader, brand angle, and evidence
- [ ] Step 2: Develop thesis, titles, and structure
- [ ] Step 3: Draft and complete editorial review
- [ ] Step 4: Generate image prompts
- [ ] Step 5: User generates images (manual, wait for user)
- [ ] Step 6: Convert images to WebP
- [ ] Step 7: Validate and preview
- [ ] Step 8: Commit and push
```

---

### Step 0: Load Preferences

Read the blog repo's CLAUDE.md for project rules:

```bash
cat "$BLOG_REPO/CLAUDE.md"
```

**Defaults** (can be overridden by user):

| Setting | Default |
|---------|---------|
| Author | 鬼哥 |
| Category | AI |
| Image format | WebP |
| Cover filename | cover.webp |
| Visual direction | Adaptive: choose from local Guige image skills by article content |

Read `references/guige-editorial-guide.md` before planning or drafting an article.

### Step 1: Define Reader, Brand Angle, and Evidence

| User Input | Action |
|------------|--------|
| A topic/idea (string) | Research the topic, then write article |
| A markdown file path | Use as article content, validate frontmatter |
| An existing post directory | Skip to Step 6 (image conversion) |
| `/blog-post` with no args | Ask user what they want to write about |

Before research, create an internal editorial brief. Do not put this planning block in the published article.

```markdown
Reader: <the specific AI/technology practitioner this article serves>
Reader situation: <the problem, decision, or conversation they are facing>
Surface topic: <what happened or what the article appears to discuss>
Core thesis: <one arguable sentence, not a topic label>
Guige angle: <what years of technical practice make visible here>
Reader gain: <new judgment, reusable method, or useful information>
Share trigger: <why a reader would send this to one specific colleague>
Evidence needed: <facts, sources, examples, counterexamples>
```

The article must have one primary reader and one core thesis. If the thesis could be agreed with before reading the article, it is probably too generic.

**Research and evidence rules**:

1. Gather primary sources, concrete examples, relevant data, and credible opposing views.
2. Separate verified facts, personal interpretation, and inference in the notes.
3. Never invent first-hand experience, conversations, results, quotations, or statistics to make the story stronger.
4. When the topic is current or factual claims may have changed, verify them before drafting.
5. Research until the thesis can be supported and challenged, not until every corner of the topic has been summarized.

**If user provides a URL or reference content**: Extract and summarize key points as source material.

### Step 2: Develop Thesis, Titles, and Structure

#### 2.1 Stress-test the thesis

Answer these questions before writing:

- What is the article's single strongest claim?
- What would an informed skeptic say?
- Which evidence could change the conclusion?
- Why is Guige the right person to make this observation?
- What should the reader think or do differently afterward?

If the article merely reports what happened, add a useful interpretation. If there is no defensible interpretation, publish a concise news note instead of stretching it into an essay.

#### 2.2 Run the title lab

Generate 8-12 working titles across at least four approaches:

- Direct judgment: state the sharpest defensible conclusion
- Conflict or tension: expose a tradeoff practitioners recognize
- Concrete result: lead with a verified number, consequence, or decision
- Narrative curiosity: reveal the setup but reserve the deeper meaning
- Veteran perspective: show what experience changes about the interpretation

Shortlist three titles and score each with the rubric in `references/guige-editorial-guide.md`. Select the strongest truthful title, not the loudest one. A title must create curiosity without withholding the article's subject or making a promise the body cannot fulfill.

#### 2.3 Design the reading experience

Choose the structure that fits the material. Do not force every article into the same template.

| Article type | Recommended structure |
|--------------|-----------------------|
| Technical judgment | Real situation -> common interpretation -> Guige's disagreement -> evidence -> practical consequence |
| Tool or product analysis | User problem -> hands-on observation -> what works -> hidden cost -> who should use it |
| Industry commentary | Event -> why the obvious reading is incomplete -> underlying mechanism -> second-order effect |
| Tutorial | Painful task -> smallest working path -> key decisions -> failure cases -> reusable checklist |
| Reflective essay | Concrete scene -> tension -> widening interpretation -> restrained reversal -> opening callback |

Plan these elements before drafting:

- One opening scene, conflict, or surprising fact
- Two to four evidence-backed movements in the argument
- At least one credible counterargument or limitation
- Two to four quotable sentences that emerge naturally from the reasoning
- One reusable artifact when appropriate: checklist, model, comparison, code, or decision rule
- A conclusion that changes or deepens the meaning of the opening

#### 2.4 Create the post directory

1. **Generate slug**: kebab-case, 2-4 English words (e.g., `karpathy-llm-wiki`, `gemma4-analysis`)

2. **Create directory**:

```bash
mkdir -p "$BLOG_REPO/content/post/<slug>"
```

3. **Verify no conflict**:

```bash
ls "$BLOG_REPO/content/post/<slug>/"
```

### Step 3: Draft and Complete Editorial Review

The brand promise is: **an experienced AI/technology practitioner helps readers see what the excitement leaves out.** The voice is restrained and professional, with dry humor, self-deprecation, precise analogies, and occasional setup-payoff callbacks.

**Frontmatter template** (YAML, between `---` delimiters):

```yaml
---
title: "从标题实验室选出的最终标题"
description: "120 字以内，独立表达文章对象、核心冲突和读者收益；不得重复标题或制造正文无法兑现的悬念。"
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

#### Opening: earn attention

Draft three openings, then keep the one that best combines specificity, tension, and trust. Good openings usually begin with a real scene, a concrete contradiction, a costly mistake, or a defensible observation. Within the first 150 Chinese characters, make clear what the article is about and why the reader should continue.

Avoid generic throat-clearing, invented drama, unsupported numbers, and formulas such as “你以为 X，其实 Y” unless the contrast is genuinely surprising.

#### Body: deliver judgment, not coverage

- Build each section around a claim, evidence, and consequence.
- Use concrete scenes and examples before abstract explanation when possible.
- Distinguish observation from opinion; link claims to sources where appropriate.
- Include uncertainty, tradeoffs, and failure conditions. Veteran credibility comes from knowing where an idea stops working.
- Delete background knowledge the target reader already knows unless it is needed for the argument.
- Let memorable lines summarize earned reasoning. Do not insert slogans that the article has not proved.

#### Humor: setup, turn, and callback

- Prefer dry understatement, precise analogy, self-deprecation, and the occasional callback.
- Humor should reveal a truth or release tension; it must not interrupt technical clarity.
- One good line is better than jokes in every paragraph.
- Do not imitate trending slang, force punchlines, ridicule beginners, or turn confidence into arrogance.
- An O. Henry-style turn means the ending changes how the opening is understood. It does not require a surprise twist in every article.

#### Ending: create resonance and utility

Choose the ending that the argument has earned:

- Callback: return to the opening scene with a deeper interpretation
- Decision rule: give practitioners a concise rule they can apply
- Practical checklist: compress a complex method into a reusable artifact
- Open consequence: show what changes next without fake urgency

Do not end with a generic summary, engagement bait, or “收藏起来以后用”. A reader should want to share because the article expresses something useful or difficult to articulate, not because the article asks to be shared.

---

**Formatting follows meaning**:

- 口语化但有技术深度，偶尔幽默
- Use bold sparingly for conclusions and decision rules, normally no more than one key emphasis per short section
- Use tables only for genuine comparison, code blocks only for executable or structurally useful content, and lists only when sequence or scanning matters
- Use descriptive subheadings; avoid uniformly clever, symmetrical, or clickbait-style headings
- Use section dividers only when the argument makes a substantial turn
- 图片引用格式：`![描述](filename.webp)`
- 文章末尾附参考资料链接

**反模式（写完自查是否中招）**：

- ❌ 开头"本文将介绍..."、"今天我们来聊..."（零钩子）
- ❌ 中间写成维基百科式的综述（没观点 = 没增量）
- ❌ 结尾"以上就是全部内容，谢谢阅读"（没 takeaway）
- ❌ 堆砌 ChatGPT 味的排比短句（"它不仅 X，还 Y，更重要的是 Z"）
- ❌ 每个小标题都工整对仗——读起来像目录，不像文章
- ❌ 先决定一个耸动结论，再挑选支持它的事实
- ❌ 冒充亲历、编造对话，或把公开材料写成个人实测
- ❌ 每隔几段强行造金句、抖包袱、要求读者收藏转发
- ❌ 把“老兵视角”写成居高临下，或用资历代替论证

**Image placement**: Plan only images that improve comprehension, memory, or emotional rhythm. A short post may need only a cover; a dense technical article may need several diagrams. For each image, note:
- Filename (kebab-case, `.webp` suffix)
- Position in article (after which section)
- What it should depict

Write the article to: `$BLOG_REPO/content/post/<slug>/index.md`

Before planning images, run all four editorial passes in `references/guige-editorial-guide.md`: truth and evidence, brand and argument, reading and voice, utility and spread. Then:

1. Score the article with the 40-point release scorecard and report the scores to the user.
2. If it fails a threshold, revise the two lowest-scoring dimensions and score it again.
3. Run the de-AI pass to remove repetitive sentence shapes, mechanical contrasts, generic transitions, and slogan-heavy endings.
4. Treat the article as stable only after it clears the release thresholds. Generate images from this stable version.

### Step 4: Generate Image Prompts

Create `image-prompts.md` in the same post directory. This file serves as a specification for the user to generate images with AI tools.

**Template**:

```markdown
# 文章配图生成 Prompt

生成后将图片保存到本目录，格式为 .webp 或 .png（会自动转为 .webp），文件名与文章中引用一致。

## 视觉方案

- Primary skill: `<guige-infographic | guige-hand-write-pic | guige-disassembly-diagram | guige-svg | guige-imagen>`
- Primary style/layout/aspect: `<selected style, layout, mode, theme, and aspect>`
- Why: `<why this visual direction fits this article>`
- Per-image overrides: `<none, or list filename -> skill/style override>`

---

## 1. cover.webp — 文章封面

Skill/style: `<skill> / <style-or-mode> / <aspect>`
Role: cover
Intent: `<what the cover must communicate>`

{prompt}

---

## 2. <filename>.webp — <描述>

Skill/style: `<skill> / <style-or-mode> / <aspect>`
Role: `<section explainer | comparison | timeline | architecture | teardown | metaphor | ...>`
Intent: `<what this image must communicate>`

{prompt}

...

---

## 使用说明

1. 将上述 prompt 分别输入 AI 图片生成工具（如 Midjourney, DALL-E, Ideogram 等）
2. 默认使用 9:16 竖图；如果 prompt 中指定 16:9、1:1 或 SVG，则按 prompt 的画幅执行
3. 生成后保存到本目录（PNG 或 WebP 均可，后续会统一转为 WebP）
4. 文章中已经用 `![描述](文件名.webp)` 格式引用了这些图片
```

**Adaptive image prompt style guide**:

Before writing `image-prompts.md`, choose a visual direction from the local Guige image skill set. Read `references/style-guide.md` for the selection matrix and prompt contracts.

1. Analyze the article's topic, audience, emotional tone, and image plan.
2. Select one primary visual skill/style for the whole post to keep the article coherent.
3. Override per image only when the image's job clearly differs from the article-level direction, such as a teardown diagram inside a warm essay.
4. In `image-prompts.md`, add a short `## 视觉方案` section before the image list:
   - `Primary skill`: one of `guige-infographic`, `guige-hand-write-pic`, `guige-disassembly-diagram`, `guige-svg`, or `guige-imagen`
   - `Primary style/layout/aspect`: selected options, if applicable
   - `Why`: one sentence explaining why this fits the article
   - `Per-image overrides`: list only images that use another skill/style
5. For each image prompt, include a compact metadata line before the prompt:
   - `Skill/style`: e.g. `guige-hand-write-pic / hand-drawn-edu / portrait`
   - `Role`: cover, section explainer, comparison, timeline, architecture, teardown, metaphor, etc.
6. Do not default to the old dark-tech palette. Use `dark-terminal`, `cyberpunk-neon`, `technical-schematic`, or `guige-svg` `dark-tech` only when the content actually calls for code, infrastructure, terminal logs, cybersecurity, or futuristic tech.
7. Text is allowed when it improves clarity; specify exact wording and keep it short and legible.
8. Blog images default to `9:16` portrait for mobile reading. Use `16:9` for architecture diagrams, SVG exports, and dense technical maps when landscape is more readable.

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
ls "$BLOG_REPO/content/post/<slug>"/*.{png,jpg,jpeg} 2>/dev/null
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

1. Check frontmatter completeness: title, description, date, slug, image, categories, tags.
2. Check all images referenced in the article exist as `.webp` files.
3. Check `cover.webp` exists (required for announcement system).
4. Confirm images still match the final title and thesis. If the article changed materially after Step 3, repeat the editorial scorecard before publishing.
5. Optionally run Hugo to verify:

```bash
cd "$BLOG_REPO"
hugo server -D
# Then user can preview at http://localhost:1313/p/<slug>/
```

### Step 8: Commit and Push

```bash
cd "$BLOG_REPO"

# Stage all post files (article + images + prompts)
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

## Quick Commands

| Command | Effect |
|---------|--------|
| `/blog-post <topic>` | Full workflow: research → write → images → publish |
| `/blog-post <file.md>` | Import existing markdown as blog post |
| `/blog-post --images <slug>` | Convert images for existing post |
| `/blog-post --publish <slug>` | Commit and push the post to the Hugo site |

## File Structure Reference

```
content/post/<slug>/
├── index.md              # Article (frontmatter + markdown)
├── image-prompts.md      # Image generation prompts
├── cover.webp            # Cover image (required)
└── *.webp                # Inline images
```
