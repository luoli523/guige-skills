# Prompt Template

Use this template to create `prompts/hand-write-pic.md`.

```markdown
Create a one-page educational visual summary.

Image settings:
- Layout: {layout}
- Style: {style}
- Aspect ratio: {aspect}
- Language: {language}
- Density: {density}

Style:
Use the selected visual style: {style}.
Style guidance: {style guidance}

If style is `hand-drawn-edu` or unspecified, use the default warm cream paper background (#F5F0E8), clean sketchnote style with slight hand-drawn wobble, pastel educational cards, and a high-quality slide summary feel.
If style is `chubby-sketch`, create a bright white rounded-card hand-drawn knowledge poster inspired by `references/chubby-sketch-style.jpeg`: oversized rounded black marker title, blue wavy underlines, compact stacked modules, dotted dividers, pastel numbered circles, pill labels, black-outline icons, sparkles/checkmarks/flowers, and optional unbranded cute cat helper doodles.
For other styles inherited from `guige-infographic`, apply only the visual treatment while preserving the one-page educational-summary structure.
No bundled Gui Ge character, no `鬼哥` narrator, no orange headband, no blue hoodie, no guitar prop. Do not add a recurring mascot except when `chubby-sketch` explicitly calls for an unbranded cute cat helper, or when the user explicitly switches to `guige-infographic`.

Density:
Use the selected density: {density}.
Density guidance: {density guidance}

For `normal` density, create a clear sketchnote summary with 3-6 visual sections, short labels, visual metaphors, and generous whitespace.
For `high` density, create a compact high-information hand-drawn infographic: 6-8 modules in a tight modular grid, small but readable text, metric chips, quote strips, process boxes, comparison cells, warning/takeaway blocks, and minimal decorative whitespace.

Color:
For `hand-drawn-edu`, use pastel rounded cards for sections:
light blue #A8D8EA, mint #B5E5CF, lavender #D5C6E0, peach #F4C7AB;
coral red #E8655A for highlights; black text/outlines; warm gray #6B6B6B annotations.
For `chubby-sketch`, use a bright white or very light warm background (#FCFBF7), black marker outlines, blue #4A90E2 wavy underlines and borders, pastel chips in soft yellow #FFE89A, pale pink #F7C6D9, light blue #CFE8FF, mint #D7F2DD, and small warm accent marks in red/yellow.
For other styles, adapt the palette to the selected style while keeping high contrast and legible text.

Design:
Visual-first. Use icons, diagrams, symbolic objects, or style-appropriate visual metaphors instead of long text.
Clear structure at a glance (flow, comparison, grouped cards, etc.).
Separate sections with rounded boxes, bubbles, or dashed frames.
Connect sections with arrows, paths, lines, or other style-appropriate connectors + short labels.
If density is `high`, prioritize information architecture over decoration: use compact modules, grouped labels, dense callouts, exact numbers, and short copied quotes where important.

Typography:
Centered bold title on top, rendered in the selected style.
Inside sections: bold keywords + compact labels (2-5 words), with annotation styling adapted to the selected style.
If density is `high`, labels may be longer when needed for factual clarity, but must remain concise and legible.

Details:
For `hand-drawn-edu`, use slightly imperfect color fill and small doodles (stars, arrows, underlines).
For `chubby-sketch`, use dotted horizontal separators, dashed vertical splits, rounded pill boxes, numbered circles, handwritten micro-bullets, playful speech bubbles, tiny sparkle/flower/star doodles, and occasional cute cat teacher/helper doodles that do not carry Gui Ge branding.
For other styles, use small decorative details that match the selected style.
If density is `normal`, keep plenty of whitespace and a clean layout.
If density is `high`, reduce oversized doodles, empty margins, and footer space so the page can carry more content while still feeling organized.

Footer:
Add one bold centered takeaway sentence at the bottom.
If density is `high`, keep the footer optional and one line only; omit it when it would crowd the content modules.

Content:
{structured content}
```

## Structuring Rules

- For `normal` density, compress the source into 3-6 visual sections.
- For `high` density, structure the source into 6-8 compact visual modules.
- Use section labels of 2-5 words when possible; in `high` density, allow 3-6 concise labels per module when needed.
- Preserve important numbers exactly.
- Use icons and diagram metaphors before adding explanatory text.
- Make the footer takeaway one sentence, bold, and centered in `normal` density; make it optional in `high` density.
- Avoid photorealistic rendering and logo-like marks. Stylized 3D is allowed only when the selected style calls for it, such as `claymation`.
- Avoid Gui Ge/`鬼哥` character references by default; this skill is for unbranded hand-drawn summaries.
