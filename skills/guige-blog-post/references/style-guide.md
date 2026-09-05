# Blog Visual Style Guide

## Adaptive Visual Direction

Blog images should adapt to the article instead of always using a dark technology look. Choose from the local Guige image skill set, then write prompts that follow the selected skill's visual contract.

### Selection Matrix

| Article / image need | Preferred skill | Recommended style / options | Use when |
|----------------------|-----------------|-----------------------------|----------|
| High-density article summary, product analysis, trend explainer | `guige-infographic` | `dense-modules` + `guige-journal`, `clean-explainer`, `social-pop`, or `lab-notes` | The image should summarize many points in one shareable poster |
| Warm knowledge card, practical checklist, essay-like concept explainer | `guige-hand-write-pic` | `hand-drawn-edu`, `chubby-sketch`, `morandi-journal`, or `craft-handmade` | The article is educational, reflective, or non-hardcore technical |
| Code, benchmark, CLI, infrastructure, model internals | `guige-infographic` or `guige-hand-write-pic` | `lab-notes`, `dark-terminal`, `technical-schematic`, or `pop-laboratory` | Technical precision matters more than warmth |
| Architecture, workflow, dependency map, timeline, comparison matrix | `guige-svg` | Select the matching diagram type; use the dark technical palette only for infrastructure/code | A directly authored editable diagram is better than a generated illustration |
| Product anatomy, hardware, physical objects, model/system component teardown | `guige-disassembly-diagram` | `hybrid`, `exploded`, or `cutaway`; light technical education poster | The image needs labeled parts, internals, material cues, or working principle |
| Emotional cover, metaphor, story scene, abstract article mood | `guige-imagen` | Natural editorial illustration, watercolor, claymation, bold graphic, cinematic, or other article-specific style | The image should create a first-glance mood rather than explain details |
| Personal life, travel, memory, family, reflective writing | `guige-hand-write-pic` or `guige-imagen` | `storybook-watercolor`, `craft-handmade`, `morandi-journal`, warm editorial illustration | Avoid dark tech unless the article itself is about technology |
| Strong opinion, social sharing, contrarian argument | `guige-infographic` | `social-pop`, `bold-graphic`, `retro-pop-grid`, or `comparison-board` | The visual needs punch, contrast, and fast comprehension |

### Selection Rules

1. Pick one primary skill/style for the article.
2. Use per-image overrides only when the image role changes substantially.
3. Prefer light or warm styles for general essays, education, life, and reflective posts.
4. Prefer technical styles for code, agents, models, tools, architecture, and benchmarks.
5. Prefer `guige-svg` when exact layout, editable output, or legible diagrams matter.
6. Prefer `guige-disassembly-diagram` for object/system anatomy and component labels.
7. Use dark palettes only when justified by the content, not as the default blog identity.

### Typography

| Role | Font |
|------|------|
| Body / Headings | Noto Serif SC |
| Code / UI labels | JetBrains Mono |

### Image Prompt Conventions

Each prompt should start with a compact routing header:

```text
Skill/style: <skill> / <style-or-mode> / <aspect>
Role: <cover | section explainer | comparison | timeline | architecture | teardown | metaphor>
Intent: <one sentence describing what this image must communicate>
```

Then write the actual image prompt using the selected skill's vocabulary. Keep the prompt content-specific: name the article's core entities, visual metaphors, labels, and structure. Do not paste a generic dark-tech suffix.

**Cover images**: Should be visually striking and convey the article's core concept at a glance. Text is allowed only when it functions as a short title or label and the exact wording is specified.

**Diagram images**: Use `guige-svg` for precise editable diagrams or `guige-infographic` / `guige-hand-write-pic` for generated explanatory diagrams. Choose the layout from the content: flowchart, sequence, structural, timeline, matrix, architecture, mind map, state machine, data flow, or illustrative.

**Comparison images**: Split-screen or side-by-side layout. Use color contrast to distinguish sides.

**Teardown images**: Use `guige-disassembly-diagram` and require clear Simplified Chinese labels, readable callouts, exploded/cutaway structure when useful, and no overlapping text.

**Metaphor images**: Use `guige-imagen` or a gentle `guige-hand-write-pic` style. Keep the metaphor grounded in the article's actual argument.

### Image Specifications

| Property | Value |
|----------|-------|
| Format | WebP (q80 via cwebp) |
| Default aspect ratio | 9:16 for blog reading; use 16:9 when the selected skill/layout is more readable in landscape |
| Min resolution | At least 1080px on the short edge for raster images |
| Naming | kebab-case, descriptive |
| Cover filename | `cover.webp` (mandatory) |

### Writing Tone Reference

Based on existing posts (gemma4-analysis, cc-anatomy series):

- 技术深度 + 口语化表达
- 用数据和对比开场
- 偶尔自嘲或幽默（"本着先吹牛再干活的优良传统"）
- 大量加粗标记核心观点
- 每个章节有独立的价值，可以单独阅读
- 结尾有行动建议或前瞻
