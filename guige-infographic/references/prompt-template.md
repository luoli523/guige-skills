# Prompt Template

Use this template to create `prompts/infographic.md`.

```markdown
---
references:
  - ref_id: 01
    filename: 01-ref-guige.jpeg
    usage: style
---

Create a polished infographic in {language}.

## Image Specs

- Type: infographic
- Layout: {layout}
- Style: {style}
- Aspect ratio: {aspect}
- Language: {language}

## Visual Direction

{style guidance}

## Layout Structure

{layout guidance}

## Gui Ge Character Reference

Use the bundled reference image as the character/style anchor. Integrate a recurring Q-style Gui Ge narrator:

- sleepy half-lidded eyes
- mildly sarcastic / 吐槽 expression
- orange headband with the Chinese text "鬼哥"
- blue hoodie
- acoustic guitar as signature prop
- cute, efficient cartoon style with a clean readable silhouette and expressive face
- adapt Japanese manga-style expression effects to the content when useful: sweat drop, surprise lines, angry vein mark, speech bubble, speed lines, sparkle eyes, deadpan face, tiny chibi reaction sticker
- match expressions to meaning: surprise for key insights, sweat drop for risks, sparkle for opportunities, deadpan for product friction, speed lines for action items
- appears as a narrator, sticker, pointer, or callout host
- supports the content hierarchy and must not dominate the page

## Content

{structured content}

## Required Text Labels

{labels}

## Rendering Requirements

- Text in {language} must be legible and grouped correctly
- Preserve all important numbers exactly
- Use clear visual hierarchy
- Keep the design dense but organized
- Make it feel like a finished information graphic, not a poster or comic page
```

## Prompt Checklist

- The prompt references `refs/01-ref-guige.jpeg` in frontmatter.
- The prompt includes the Gui Ge character traits in text.
- The prompt includes the chosen layout, style, aspect ratio, and selected language requirement.
- The prompt includes the structured content and required labels.
- The prompt explicitly asks for readable text in the selected language and exact preservation of key numbers.
