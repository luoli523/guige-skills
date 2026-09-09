---
name: guige-blog-post
description: "Write engaging Chinese AI and technology blog posts in Guige's lively, experienced peer voice, drawing readers through recognizable situations, curiosity, and concrete discoveries toward useful insight; support illustration and publishing to the luoli523.github.io Hugo blog. Trigger on: /blog-post, writing blog post, publish post, write article for blog."
version: 0.5.0
---

# Blog Post Workflow

End-to-end workflow for writing, illustrating, and publishing blog posts to the Hugo blog at `luoli523.github.io`.

**Editorial priority:** Write for a person choosing to spend time with this article. Start from something they recognize or want, give them a reason to be curious, and let examples and discoveries carry the explanation. Usefulness includes recognition, understanding, enjoyment, and a new possibility—not only a completed technical task. Keep fact-checking backstage; default to an engaging blog article, with report-level detail only when the user asks for it or the article's promise requires it.

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
- [ ] Step 1: Find the reader's situation and the story worth following
- [ ] Step 2: Choose article type, titles, and structure
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

### Step 1: Find the Reader's Situation and the Story Worth Following

| User Input | Action |
|------------|--------|
| A topic/idea (string) | Research the topic, then write article |
| A markdown file path | Use as the draft; preserve the user's intended content, check frontmatter, and complete Step 3 editorial review before publishing |
| An existing post directory | Route by requested work: writing/revision uses Steps 1–3; image-only work starts at Step 6; publishing checks editorial readiness before Steps 7–8 |
| `/blog-post` with no args | Ask user what they want to write about |

Before research, make a short private writing note. These are prompts for finding the article, not headings or a form to publish.

```markdown
Reader and moment: <what someone is doing, hoping for, puzzled by, or tired of; what they already understand>
Hook: <the recognizable friction, appealing possibility, or unexpected detail that makes them care>
Thread: <the example, question, or experience that can carry the article forward>
Discovery and payoff: <what becomes clearer or newly possible along the way, and why it matters>
Material to verify: <claims to check; whether scenes are supplied experience, attributed cases, or explicit illustrations>
```

Anchor the article in one primary reader situation without narrowing every subject to an engineering task. Follow the curiosity that situation creates. A useful synthesis or explanation needs no manufactured disagreement. Use the writing routes in `references/guige-editorial-guide.md` as options, not mandatory deliverables.

**Backstage research**:

1. Gather primary sources, concrete examples, relevant data, and credible opposing views.
2. Separate verified facts, personal interpretation, and inference in the notes.
3. Never invent first-hand experience, conversations, results, quotations, or statistics to make the story stronger.
4. When the topic is current or factual claims may have changed, verify them before drafting.
5. Treat the initial answer or thesis as provisional. Research until the reader's question can be answered with adequate evidence and limits; revise the conclusion when the evidence changes it.
6. Follow the guide's backstage accuracy rules. Do not turn research notes into a methodology section by default; bring a detail into the body when the reader needs it to understand, trust, or use the point at hand.

**If user provides a URL or reference content**: Extract and summarize key points as source material.

### Step 2: Choose Article Type, Titles, and Structure

#### 2.1 Find the reason to keep reading

Answer these questions before writing:

- Where will the reader recognize their own experience or something they want to try?
- What specifically makes them want the next paragraph?
- Which example lets them watch the idea unfold rather than receive a lecture?
- What interesting discovery and useful understanding will reward that attention?
- For commentary, privately challenge the conclusion before writing; include the objection if it materially changes the reader's understanding.

If the material only supports a brief factual update, write a concise note. Do not manufacture disagreement or stretch it into an essay. Useful synthesis should resolve confusion, connect scattered information, or explain practical consequences.

#### 2.2 Run the title lab

Try a few titles suited to the material, using approaches such as:

- Direct judgment: state the sharpest defensible conclusion
- Conflict or tension: expose a tradeoff practitioners recognize
- Concrete result: lead with a verified number, consequence, or decision
- Task or question: name what the reader can accomplish or understand, with a relevant scope or constraint
- Narrative curiosity: reveal the setup but reserve the deeper meaning
- Veteran perspective: show what experience changes about the interpretation

Compare two or three promising titles using the title guidance in `references/guige-editorial-guide.md`. Choose one that combines recognizable subject, reader interest, and a promise the body fulfills. Do not manufacture suspense by hiding the subject.

#### 2.3 Design the reading experience

Choose the structure that fits the material. Do not force every article into the same template.

| Article type | Recommended structure |
|--------------|-----------------------|
| Technical judgment | Recognizable dilemma -> concrete example -> what it reveals -> a judgment that helps with the dilemma |
| Tool or product analysis | Something the reader wants to do -> follow one use case -> surprises and friction -> who would enjoy or benefit from it |
| Industry commentary | An interesting change -> where it touches everyday work or life -> what explains it -> what becomes possible or different |
| Tutorial | A result worth wanting -> first small success -> next obstacle and discovery -> the reader can try it too |
| Mechanism explainer | An intriguing everyday question -> follow one example -> reveal the mechanism when needed -> return with a clearer view |
| Engineering retrospective | A puzzling symptom -> clues and attempted explanations -> discovery -> what changed afterward |
| Reflective essay | Concrete scene -> tension -> widening interpretation -> restrained reversal -> opening callback |

Plan these elements before drafting:

- An opening that earns interest through a recognizable situation, a concrete curiosity, or a desirable result
- A thread that connects the sections through events, examples, questions, or discoveries
- Moments where the reader sees something happen or understands something new
- A payoff that answers the opening's promise and leaves an insight, possibility, or natural next action

Introduce technical detail when the unfolding example makes the reader want it. Keep enough in the body to understand and use the idea; place lengthy configurations or measurement details in an appendix when needed. Do not add a section for every profession. The article must have appeal and forward movement, but humor, suspense, and callbacks are tools to choose from, not quotas or mandatory twists.

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

The brand promise is: **鬼哥从你熟悉的场景聊起，把 AI 和技术里有意思、有用的东西讲明白，让你顺着好奇心读下去，读完觉得懂了，也想试试。** Write as a knowledgeable, interested person talking with a peer: warm, observant, opinionated where warranted, and capable of delight. Professional credibility does not require a solemn or impersonal voice.

**Frontmatter template** (YAML, between `---` delimiters):

```yaml
---
title: "从标题实验室选出的最终标题"
description: "120 字以内，独立表达文章对象、适用场景和读者收益；不得重复标题或制造正文无法兑现的悬念。"
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

The opening must give the reader a reason to care and continue. In roughly the first 150 Chinese characters, let them recognize the subject through a concrete moment, friction, surprise, or appealing result. Make the promise felt through the situation rather than announcing learning objectives. Try a couple of different openings if the first only names the topic. Do not delay a practical answer just to manufacture suspense.

Avoid generic throat-clearing, invented drama, unsupported numbers, and formulas such as “你以为 X，其实 Y” unless the contrast is genuinely surprising.

#### Body: deliver the promised reader gain

- Connect paragraphs through what just happened, what it means, and what naturally follows. Avoid repeating a claim–evidence–consequence template in every section.
- Let the reader watch a concrete example develop: a question asked, an output noticed, a choice made, a snag resolved. Use sourced material or clearly framed illustrations; never invent an author's hands-on experience.
- Explain a concept at the moment it helps the reader understand the example. Use familiar objects, active verbs, and precise analogies; clarify an analogy's limit if it could mislead here.
- Give the prose room for recognition, surprise, dry humor, and the author's observations. Interest can come from a satisfying explanation or a possibility the reader wants, not just conflict.
- Keep claims accurate and link important sources unobtrusively. State limitations where they change the point; do not append a caveat to every paragraph.
- Include the steps a promised tutorial actually needs, but keep general articles free of unsolicited environment matrices, benchmark protocols, acceptance criteria, and checklists.
- If a stretch feels like a lecture, change its example, order, or level of detail. Adding a joke to dense exposition does not fix the reading experience.

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
- ❌ 只复述材料，既没有解释增量，也没有方法、证据或决策价值
- ❌ 结尾"以上就是全部内容，谢谢阅读"（没 takeaway）
- ❌ 堆砌 ChatGPT 味的排比短句（"它不仅 X，还 Y，更重要的是 Z"）
- ❌ 每个小标题都工整对仗——读起来像目录，不像文章
- ❌ 先决定一个耸动结论，再挑选支持它的事实
- ❌ 冒充亲历、编造对话，或把公开材料写成个人实测
- ❌ 每隔几段强行造金句、抖包袱、要求读者收藏转发
- ❌ 把“老兵视角”写成居高临下，或用资历代替论证
- ❌ 用“适用人群—前置条件—证据等级—边界—验收清单”组织普通博客，写成评审报告
- ❌ 开头有故事，进入正文就连续堆概念；靠结尾补一个笑话挽救阅读体验
- ❌ 把读者场景缩减为部署、延迟、成本，忽略好奇、创作、沟通和日常使用

**Image placement**: Plan only images that improve comprehension, memory, or emotional rhythm. A short post may need only a cover; a dense technical article may need several diagrams. For each image, note:
- Filename (kebab-case, `.webp` suffix)
- Position in article (after which section)
- What it should depict

Write the article to: `$BLOG_REPO/content/post/<slug>/index.md`

Before planning images, use the editorial review in `references/guige-editorial-guide.md` to check reader connection, momentum, payoff, and backstage accuracy. Then:

1. Identify where a reader first has reason to care and where they are most likely to lose interest. Rewrite the weak stretch by changing its material, order, or explanation.
2. Confirm the article rewards the opening's promise and contains no material factual problem. Keep review notes private unless requested; do not report numerical self-scores by default.
3. Run the de-AI and read-aloud pass to remove report-like language, repetitive sentence shapes, and artificial hooks.
4. Generate images once the text reads naturally and delivers its promise. Images should enrich the experience, not compensate for a dull draft.

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
6. Do not default to a dark-tech palette. Use `dark-terminal`, `cyberpunk-neon`, `technical-schematic`, or the `guige-svg` dark technical palette only when the content actually calls for code, infrastructure, terminal logs, cybersecurity, or futuristic tech.
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
4. Confirm images still match the final title and content. Before publishing an imported or existing article, complete Step 3 editorial review if there is no review for the current text. If the article changed materially after review, repeat the reader-experience and factual checks. Image-only work does not trigger unsolicited rewriting.
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
