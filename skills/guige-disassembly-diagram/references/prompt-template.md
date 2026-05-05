# Prompt Template

Use this template to create `prompts/disassembly-diagram.md`.

```markdown
Generate a high-quality teaching science illustration / knowledge card about: {target_object}

## Image Settings

- Output language: {language}
- Aspect ratio: {aspect}
- Diagram mode: {mode}
- Image type: modern technical education infographic, product structure explainer, teardown knowledge card
- Background: clean white, light gray, or light blue-gray

## Core Goal

Show the object's overall appearance, internal structure, key components, material characteristics, and working principle. All labels, captions, title text, and flowchart text must be clear, accurate, standard Simplified Chinese.

## Visual Structure

Include these visual modules when compatible with the selected mode:

1. Main exterior view: show the complete outer form and label major external structures.
2. Exploded / disassembly view: show layered core parts and connection relationships.
3. Cutaway / half-section view: show internal layout and key structural positions.
4. Local magnification: enlarge 3-5 key details with short Chinese explanations.
5. Function area: use small icons plus short text to explain what major modules do.
6. Working-principle flowchart: use arrows to show the basic logic, for example `能量输入 -> 控制系统 -> 核心部件运行 -> 输出结果`.

## Required Content

{structured_content}

## Typography Requirements

All visible text must use clear, neat, standard Simplified Chinese typography similar to Source Han Sans / PingFang / Microsoft YaHei / SimHei.

- Title: prominent, bold, easy to read.
- Labels: medium-large, high contrast, readable at poster/card size.
- Captions: concise, grouped near the related part.
- Avoid decorative fonts, handwriting fonts, artistic fonts, ultra-thin fonts, deformed glyphs, garbled text, tiny labels, overlapping text, and illegible annotations.
- Prefer fewer, larger labels over many tiny labels when space is limited.

## Style Requirements

Modern technology feeling, clean teaching infographic style, professional and beautiful, easy to understand, suitable for classroom explanation, science articles, social media cover images, and knowledge cards.

- Clear visual hierarchy and organized modules.
- Information-rich but not cluttered.
- Accurate schematic structure with distinct layers.
- Strong material cues: metal, plastic, glass, rubber, ceramic, fabric, composite, fluid, circuit board, battery, or other relevant materials.
- Use arrows, leader lines, bracket labels, numbered callouts, and subtle color coding to clarify relationships.
- Make the final result look like a premium science explainer poster / product structure sheet.

## Accuracy Requirements

{accuracy_note}

Avoid over-artistic interpretation. Prioritize accuracy, clarity, readability, and structured explanation over decorative complexity.
```

## Prompt Checklist

- Replace `{target_object}`, `{language}`, `{aspect}`, `{mode}`, `{structured_content}`, and `{accuracy_note}`.
- Keep Chinese labels concise and large enough to read.
- Include exact required labels and flow text in the prompt.
- If exact internals are uncertain, state that the image should be a schematic explainer, not an exact engineering teardown.
- If the object has a known cross-section or exploded-view convention, specify it directly in `structured_content`.
