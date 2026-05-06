# Outline Template

Use this structure for `outline.md`.

```markdown
# Slide Deck Outline

**Topic**: [topic]
**Style**: [preset or custom]
**Dimensions**: [texture] + [mood] + [typography] + [density]
**Audience**: [audience]
**Language**: [language]
**Slide Count**: [N]
**Generated**: [YYYY-MM-DD HH:mm]

---

<STYLE_INSTRUCTIONS>
[Complete style instructions here]
</STYLE_INSTRUCTIONS>

---

## Slide 1 of N

**Type**: Cover
**Filename**: 01-slide-cover.png

// NARRATIVE GOAL
[What this slide achieves]

// KEY CONTENT
Headline: [title]
Sub-headline: [supporting line]

// VISUAL
[Specific visual composition]

// LAYOUT
Layout: title-hero
[Spatial arrangement]

## Slide X of N

**Type**: Content
**Filename**: {NN}-slide-{slug}.png

// NARRATIVE GOAL
[One message this slide delivers]

// KEY CONTENT
Headline: [narrative headline]
Sub-headline: [optional context]
Body:
- [point 1]
- [point 2]
- [point 3]

// VISUAL
[Visual metaphor, objects, diagram, or scene]

// LAYOUT
Layout: [optional layout from layouts.md]
[Composition details]

## Slide N of N

**Type**: Back Cover
**Filename**: {NN}-slide-back-cover.png

// NARRATIVE GOAL
[Meaningful closing]

// KEY CONTENT
Headline: [closing statement]
Body:
- [optional next step]

// VISUAL
[Closing visual]

// LAYOUT
Layout: closing-card
```

Rules:

- Cover and back-cover are required.
- Each content slide should have one main idea.
- Prefer 2-4 content bullets per slide.
- Preserve important facts, names, numbers, and quotes exactly.
- Use filenames matching `NN-slide-*.png`.
