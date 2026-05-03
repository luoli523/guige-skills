# Blog Visual Style Guide

## Design System: Ghost Protocol Dark Palette

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-void` | `#07090f` | Deepest background |
| `--bg-surface` | `#0d1117` | Surface background |
| `--bg-card` | `#0f151e` | Card background |
| `--teal` | `#2dd4bf` | Primary accent |
| `--amber` | `#f59e0b` | Secondary accent (tools, projects) |
| `--purple` | `#a78bfa` | Tertiary accent |
| `--red` | `#f87171` | Alert / life category |
| `--text-primary` | `#e8eaf0` | Primary text |
| `--text-secondary` | `#8b9ab0` | Secondary text |

### Typography

| Role | Font |
|------|------|
| Body / Headings | Noto Serif SC |
| Code / UI labels | JetBrains Mono |

### Image Prompt Conventions

**Standard suffix for all prompts**:
```
Style: clean tech illustration, dark mode aesthetic, minimal and elegant.
Background: deep dark navy (#07090f or #0d1117).
Primary accent: teal (#2dd4bf).
No text unless specified. 16:9 aspect ratio.
```

**Cover images**: Should be visually striking, convey the article's core concept at a glance. No text overlay.

**Diagram images**: Clean, diagrammatic style. Use teal for primary elements, amber for secondary, purple for tertiary. Dark background. Icon-based, not photorealistic.

**Comparison images**: Split-screen or side-by-side layout. Use color contrast to distinguish sides.

### Image Specifications

| Property | Value |
|----------|-------|
| Format | WebP (q80 via cwebp) |
| Aspect ratio | 16:9 |
| Min resolution | 1920x1080 |
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
