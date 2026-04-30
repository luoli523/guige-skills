# Prompt Template

Use this template to create `prompts/hand-write-pic.md`.

```markdown
Create a one-page hand-drawn educational infographic.

Image settings:
- Layout: {layout}
- Aspect ratio: {aspect}
- Language: {language}

Style:
Warm cream paper background (#F5F0E8), clean sketchnote style with slight hand-drawn wobble. No realistic elements. Looks like a high-quality slide summary.
No bundled Gui Ge character, no `鬼哥` narrator, no orange headband, no blue hoodie, no guitar prop, and no recurring mascot unless the user explicitly switches to `guige-infographic`.

Color:
Use pastel rounded cards for sections:
light blue #A8D8EA, mint #B5E5CF, lavender #D5C6E0, peach #F4C7AB.
Use coral red #E8655A for highlights (keywords, key data, checkmarks).
Main text and outlines in black, annotations in warm gray #6B6B6B.

Design:
Visual-first. Use icons, doodles, simple diagrams instead of text.
Clear structure at a glance (flow, comparison, grouped cards, etc.).
Separate sections with rounded boxes, bubbles, or dashed frames.
Connect sections with hand-drawn wavy arrows + short labels.

Typography:
Centered bold hand-drawn title on top.
Inside sections: bold keywords + small gray labels (2-5 words).

Details:
Slightly imperfect color fill (not fully inside outlines).
Add small doodles (stars, arrows, underlines).
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
- Avoid realistic rendering, photo texture, 3D realism, and logo-like marks.
- Avoid Gui Ge/`鬼哥` character references by default; this skill is for unbranded hand-drawn summaries.
