# Prompt Template

Use this template to create `prompts/hand-write-pic.md`.

```markdown
Create a one-page educational visual summary.

Image settings:
- Layout: {layout}
- Style: {style}
- Aspect ratio: {aspect}
- Language: {language}

Style:
Use the selected visual style: {style}.
Style guidance: {style guidance}

If style is `hand-drawn-edu` or unspecified, use the default warm cream paper background (#F5F0E8), clean sketchnote style with slight hand-drawn wobble, pastel educational cards, and a high-quality slide summary feel.
For other styles inherited from `guige-infographic`, apply only the visual treatment while preserving the one-page educational-summary structure.
No bundled Gui Ge character, no `鬼哥` narrator, no orange headband, no blue hoodie, no guitar prop, and no recurring mascot unless the user explicitly switches to `guige-infographic`.

Color:
For `hand-drawn-edu`, use pastel rounded cards for sections:
light blue #A8D8EA, mint #B5E5CF, lavender #D5C6E0, peach #F4C7AB;
coral red #E8655A for highlights; black text/outlines; warm gray #6B6B6B annotations.
For other styles, adapt the palette to the selected style while keeping high contrast and legible text.

Design:
Visual-first. Use icons, diagrams, symbolic objects, or style-appropriate visual metaphors instead of long text.
Clear structure at a glance (flow, comparison, grouped cards, etc.).
Separate sections with rounded boxes, bubbles, or dashed frames.
Connect sections with arrows, paths, lines, or other style-appropriate connectors + short labels.

Typography:
Centered bold title on top, rendered in the selected style.
Inside sections: bold keywords + compact labels (2-5 words), with annotation styling adapted to the selected style.

Details:
For `hand-drawn-edu`, use slightly imperfect color fill and small doodles (stars, arrows, underlines).
For other styles, use small decorative details that match the selected style.
Keep plenty of whitespace, clean layout.

Footer:
Add one bold centered takeaway sentence at the bottom.

Content:
{structured content}
```

## Structuring Rules

- Compress the source into 3-6 visual sections.
- Use section labels of 2-5 words when possible.
- Preserve important numbers exactly.
- Use icons and diagram metaphors before adding explanatory text.
- Make the footer takeaway one sentence, bold, and centered.
- Avoid photorealistic rendering and logo-like marks. Stylized 3D is allowed only when the selected style calls for it, such as `claymation`.
- Avoid Gui Ge/`鬼哥` character references by default; this skill is for unbranded hand-drawn summaries.
