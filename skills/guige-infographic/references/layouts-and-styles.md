# Layouts And Styles

Standalone design vocabulary for `guige-infographic`.

## 中文参数速查

每次运行前先把下面选项用中文展示给用户。用户可以回复编号，也可以直接传 `--layout`、`--style`、`--aspect`、`--lang`。

默认参数：`layout=L1 style=S1 aspect=A2 lang=G1`

默认组合：`dense-modules / guige-journal / landscape / zh`

### Layout 布局选项

| 编号 | 参数 | 中文说明 |
|------|------|----------|
| L1 | `dense-modules` | 默认。高密度模块长图，适合访谈总结、产品分析、信息量大的文章 |
| L2 | `bento-dashboard` | Bento 仪表盘，适合清爽概览和汇报页 |
| L3 | `technical-map` | 技术关系图，适合架构、能力层、Agent 工作流 |
| L4 | `timeline-road` | 时间线/路线图，适合流程、发布节奏、迁移路径 |
| L5 | `comparison-board` | 对比看板，适合 A/B、工具/模型优劣对比 |
| L6 | `linear-progression` | 线性步骤，适合教程和顺序流程 |
| L7 | `binary-comparison` | 二元对比，适合 before/after、正反观点 |
| L8 | `comparison-matrix` | 多因素矩阵，适合多个方案横向比较 |
| L9 | `hierarchical-layers` | 层级结构，适合成熟度、优先级、金字塔 |
| L10 | `tree-branching` | 树状分类，适合分类体系和决策分支 |
| L11 | `hub-spoke` | 中心辐射，适合一个核心观点连接多个影响 |
| L12 | `structural-breakdown` | 结构拆解，适合系统组成、模块拆解 |
| L13 | `iceberg` | 冰山图，适合表层现象和深层原因 |
| L14 | `bridge` | 问题到方案，适合痛点-解法叙事 |
| L15 | `funnel` | 漏斗，适合筛选、转化、收敛过程 |
| L16 | `isometric-map` | 等距地图，适合平台生态和空间关系 |
| L17 | `dashboard` | 指标仪表盘，适合 KPI、数据、评分 |
| L18 | `periodic-table` | 周期表，适合能力清单和分类集合 |
| L19 | `comic-strip` | 漫画分镜，适合故事化解释和连续场景 |
| L20 | `story-mountain` | 故事山，适合矛盾升级和项目叙事 |
| L21 | `jigsaw` | 拼图，适合互相依赖的组成部分 |
| L22 | `venn-diagram` | 韦恩图，适合交集、边界、重叠关系 |
| L23 | `winding-roadmap` | 弯曲路线图，适合非线性旅程和规划 |
| L24 | `circular-flow` | 循环流，适合反馈循环和持续迭代 |

### Style 风格选项

| 编号 | 参数 | 中文说明 |
|------|------|----------|
| S1 | `guige-journal` | 默认。鬼哥手账风，温暖、亲和、适合高密度中文信息图 |
| S2 | `lab-notes` | 实验室笔记风，适合 benchmark、技术指标、架构内容 |
| S3 | `social-pop` | 社交传播风，大数字、强对比、适合小红书/朋友圈传播 |
| S4 | `clean-explainer` | 清爽讲解风，适合管理层汇报和易读概览 |
| S5 | `dark-terminal` | 深色终端风，适合 CLI、代码、日志、基础设施 |
| S6 | `craft-handmade` | 手工纸艺风，温和、轻松、亲切 |
| S7 | `claymation` | 黏土动画风，柔软 3D、趣味感强 |
| S8 | `kawaii` | 可爱日系风，适合轻松科普和表情贴纸 |
| S9 | `storybook-watercolor` | 水彩绘本风，适合故事化和温柔叙事 |
| S10 | `chalkboard` | 黑板粉笔风，适合教学讲解 |
| S11 | `cyberpunk-neon` | 赛博霓虹风，适合未来感和强视觉冲击 |
| S12 | `bold-graphic` | 粗线漫画风，适合观点鲜明的内容 |
| S13 | `aged-academia` | 复古学术风，适合研究、历史、论文感内容 |
| S14 | `corporate-memphis` | 商务孟菲斯风，适合产品汇报和组织沟通 |
| S15 | `technical-schematic` | 技术蓝图风，适合系统图、工程图 |
| S16 | `origami` | 折纸几何风，适合抽象概念和模块结构 |
| S17 | `pixel-art` | 像素风，适合复古、游戏化、轻量主题 |
| S18 | `ui-wireframe` | UI 线框风，适合产品流程和界面说明 |
| S19 | `subway-map` | 地铁线路风，适合路径、依赖和路线关系 |
| S20 | `ikea-manual` | 宜家说明书风，适合极简步骤和操作指南 |
| S21 | `knolling` | 平铺整理风，适合组件和资料清单 |
| S22 | `lego-brick` | 积木模块风，适合组合、搭建、系统组件 |
| S23 | `pop-laboratory` | 流行实验室风，适合技术指标和强视觉标注 |
| S24 | `morandi-journal` | 莫兰迪手账风，温和克制、接近鬼哥默认风 |
| S25 | `retro-pop-grid` | 复古波普网格风，适合强对比观点图 |
| S26 | `hand-drawn-edu` | 手绘教育风，适合课程、知识卡、概念解释 |

### Aspect 画幅选项

| 编号 | 参数 | 中文说明 |
|------|------|----------|
| A1 | `portrait` | 9:16 竖版长图，适合移动端和高密度信息图 |
| A2 | `landscape` | 默认。16:9 横版，适合会议、PPT、网页展示 |
| A3 | `square` | 1:1 方图，适合封面和社交缩略图 |
| A4 | 自定义比例 | 例如 `3:4`、`4:3`、`2.35:1` |

### Lang 语言选项

| 编号 | 参数 | 中文说明 |
|------|------|----------|
| G1 | `zh` | 默认。中文 |
| G2 | `en` | 英文 |
| G3 | `ja` | 日文 |
| G4 | `ko` | 韩文 |
| G5 | 自定义语言 | 例如 `fr`、`de`、`Thai` |

### 回复格式示例

```text
layout=L1 style=S1 aspect=A2 lang=G1
```

或：

```text
--layout dense-modules --style guige-journal --aspect landscape --lang zh
```

## Layout Values

### Core Gui Ge Layouts

| Layout | Best For |
|--------|----------|
| `dense-modules` | High-density Chinese long images, research summaries, product strategy notes |
| `bento-dashboard` | Cleaner overview pages with 5-6 mixed-size cards |
| `technical-map` | Architecture, capability maps, agent workflows, system relationships |
| `timeline-road` | Release history, process walkthroughs, migration stories |
| `comparison-board` | A/B choices, model/tool comparisons, pros/cons |

### Extended Layout Gallery

| Layout | Best For |
|--------|----------|
| `linear-progression` | Step-by-step processes, tutorials, sequential logic |
| `binary-comparison` | Before/after, A vs B, pros/cons |
| `comparison-matrix` | Multi-factor comparisons across several options |
| `hierarchical-layers` | Pyramids, maturity levels, priority tiers |
| `tree-branching` | Categories, taxonomies, decision branches |
| `hub-spoke` | One central concept with surrounding related points |
| `structural-breakdown` | Exploded views, anatomy, layered systems |
| `iceberg` | Surface symptoms vs hidden causes |
| `bridge` | Problem-to-solution narrative |
| `funnel` | Filtering, conversion, narrowing decisions |
| `isometric-map` | Spatial relationships, platform maps, ecosystems |
| `dashboard` | Metrics, KPIs, scorecards |
| `periodic-table` | Categorized collections, capability inventories |
| `comic-strip` | Narrative sequences with character reactions |
| `story-mountain` | Narrative tension, project journey, escalation |
| `jigsaw` | Interdependent parts that form a whole |
| `venn-diagram` | Overlap and boundary analysis |
| `winding-roadmap` | Nonlinear journey, milestones, planning path |
| `circular-flow` | Cycles, feedback loops, repeated workflows |

## Layout Guidance

### dense-modules

- 6-7 compact modules
- strong top title zone
- metric cards, quote strips, process boxes, warning/takeaway blocks
- small but readable text
- use for launches, product analysis, technical summaries, trend explainers

### bento-dashboard

- 5-6 uneven cards
- one hero card plus supporting cards
- larger whitespace and fewer details
- use for executive summaries and general audience explainers

### technical-map

- nodes, arrows, swimlanes, labels
- benchmark numbers in technical badges
- use for architecture, agent workflows, model capability maps

### timeline-road

- vertical or winding path
- milestones, numbered steps, before/after states
- use for tutorials, releases, migration stories

### comparison-board

- 2-4 columns
- scoring rows, pros/cons, metric highlights
- use for A/B comparisons, model comparisons, tool choices

## Style Values

### Core Gui Ge Styles

| Style | Description |
|-------|-------------|
| `guige-journal` | Warm bullet-journal style with Gui Ge narrator stickers and hand-drawn product thinking |
| `lab-notes` | Technical benchmark style with grids, annotations, metric badges |
| `social-pop` | High-shareability social card style with bolder contrast and large numbers |
| `clean-explainer` | Calm educational style with larger labels and fewer decorative elements |
| `dark-terminal` | Developer-focused dark style for CLI, code, logs, infra |

### Extended Style Gallery

| Style | Description |
|-------|-------------|
| `craft-handmade` | Paper craft, hand-cut shapes, friendly handmade texture |
| `claymation` | Soft 3D clay objects, stop-motion feel |
| `kawaii` | Cute Japanese-inspired pastel style, expressive reaction stickers |
| `storybook-watercolor` | Soft watercolor, gentle storytelling, warm narrative tone |
| `chalkboard` | Chalk marks on dark board, classroom explanation feel |
| `cyberpunk-neon` | Neon tech glow, high contrast, futuristic |
| `bold-graphic` | Comic-like bold shapes, halftone accents, strong headline energy |
| `aged-academia` | Vintage research notes, sepia paper, archival diagrams |
| `corporate-memphis` | Flat modern business graphics, geometric color blocks |
| `technical-schematic` | Blueprint-like technical linework, labels, precise diagrams |
| `origami` | Folded paper geometry, sharp planes, modular structure |
| `pixel-art` | Retro 8-bit aesthetic, blocky icons, game-like signals |
| `ui-wireframe` | Grayscale UI mockup style, interface components, product flows |
| `subway-map` | Transit-map lines, station labels, route relationships |
| `ikea-manual` | Minimal line art, clean instructions, no extra decoration |
| `knolling` | Organized flat-lay composition, labeled components |
| `lego-brick` | Toy-brick construction metaphor, modular assembly |
| `pop-laboratory` | Lab manual precision with pop color highlights and coordinate marks |
| `morandi-journal` | Warm muted hand-drawn journal style, close to guige-journal but less branded |
| `retro-pop-grid` | 1970s pop color, strict grid, thick outlines |
| `hand-drawn-edu` | Pastel educational diagram style with casual hand-drawn wobble |

## Style Guidance

### guige-journal

- warm cream paper background
- muted teal, sage, terracotta, pale yellow, charcoal brown
- hand-drawn module frames, dotted lines, tabs, tape labels
- technical but human, like a premium bullet journal
- includes Gui Ge narrator stickers/callouts
- use cute, efficient cartoon expressions for Gui Ge

### lab-notes

- light gray paper with faint grid
- teal blocks, yellow highlights, red warning accents
- coordinate labels, tiny annotations, benchmark bars, terminal doodles
- best for coding, model benchmarks, infrastructure topics

### social-pop

- stronger contrast
- large numbers
- sticker-like callouts
- simplified modules
- best for mobile social posts

### clean-explainer

- calm color blocks
- larger labels
- fewer decorative elements
- best when source content is complex and readability is more important than density

### dark-terminal

- dark charcoal background
- green/teal terminal accents
- code windows, logs, CLI panels
- use only when the user explicitly wants dark technical visuals

## Aspect Values

| Aspect | Ratio | Use |
|--------|-------|-----|
| `portrait` | `9:16` | Mobile long image, high-density social sharing |
| `landscape` | `16:9` | Default. Slides, meeting decks, web sharing |
| `square` | `1:1` | Social thumbnails and compact posts |
| Custom W:H | e.g. `3:4`, `4:3`, `2.35:1` | Use exactly as provided |

## Language Values

Use any requested language. Common values:

| Value | Meaning |
|-------|---------|
| `zh` | Chinese |
| `en` | English |
| `ja` | Japanese |
| `ko` | Korean |

Keep the Gui Ge headband text `鬼哥` unchanged in every language.

## Recommendation Rules

- Use `dense-modules + guige-journal + landscape + zh` as the default combination.
- Use `dense-modules + guige-journal + portrait` when the user explicitly wants a mobile long image.
- Use `technical-map + lab-notes` when relationships, infrastructure, or benchmark systems matter most.
- Use `bento-dashboard + clean-explainer` when the user asks for a clean, readable overview.
- Use `comparison-board + lab-notes` or `comparison-matrix + corporate-memphis` for model/tool comparisons.
- Use `timeline-road + guige-journal` or `linear-progression + hand-drawn-edu` for process, launch history, or migration stories.
- Use `hub-spoke + guige-journal` for “one core idea with many implications”.
- Use `dashboard + lab-notes` for KPI-heavy content.

## Alias Mapping

Map familiar names to native Gui Ge names when useful:

| Input | Preferred Internal Choice |
|-------|---------------------------|
| `bento-grid` | `bento-dashboard` |
| `technical-schematic` layout intent | `technical-map` |
| `morandi-journal` with Gui Ge branding | `guige-journal` |
| `pop-laboratory` with benchmark-heavy content | `lab-notes` |
