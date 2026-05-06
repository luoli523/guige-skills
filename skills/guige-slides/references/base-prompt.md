Create one presentation slide image.

## Image Specifications

- Type: presentation slide
- Aspect ratio: 16:9 landscape
- Output: a complete slide image, no visible slide number, no app chrome

## Core Direction

Create a reading-friendly slide for a shareable deck. The slide must be self-explanatory, visually clear, and faithful to the source content.

## Text Rules

- Use the requested output language.
- Keep text legible.
- Title: large, bold, immediately readable.
- Body: compact and clear.
- Max 3-4 text groups per slide.
- Do not create pseudo text or malformed characters.

## Visual Rules

- One clear message per slide.
- Use strong visual hierarchy and generous margins.
- Use diagrams, symbolic objects, icons, visual metaphors, charts, or scenes where helpful.
- Avoid realistic photos unless the chosen style explicitly calls for a realistic visual treatment.
- Avoid logos unless the user provided or requested them.

## STYLE_INSTRUCTIONS

Copy the complete `<STYLE_INSTRUCTIONS>...</STYLE_INSTRUCTIONS>` block from `outline.md`.

## SLIDE CONTENT

Insert the slide-specific entry from `outline.md`.

## References

If prompt frontmatter lists reference images, follow their `usage` field:

- `direct`: use as image reference if backend supports it.
- `style`: extract visual traits.
- `palette`: use colors only.
