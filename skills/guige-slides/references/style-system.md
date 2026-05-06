# Style System

`guige-slides` uses style presets made from four dimensions: texture, mood, typography, and density.

## Presets

| Preset | Dimensions | Best For |
|--------|------------|----------|
| `blueprint` | grid + cool + technical + balanced | architecture, systems, technical explainers |
| `chalkboard` | organic + warm + handwritten + balanced | education, classroom, tutorials |
| `corporate` | clean + professional + geometric + balanced | business, investor, proposal decks |
| `minimal` | clean + neutral + geometric + minimal | executive briefings |
| `sketch-notes` | organic + warm + handwritten + balanced | friendly learning summaries |
| `hand-drawn-edu` | organic + macaron + handwritten + balanced | process explainers, onboarding |
| `watercolor` | organic + warm + humanist + minimal | lifestyle, wellness, travel |
| `dark-atmospheric` | clean + dark + editorial + balanced | entertainment, gaming, cinematic topics |
| `notion` | clean + neutral + geometric + dense | SaaS, product, metrics, dashboards |
| `bold-editorial` | clean + vibrant + editorial + balanced | product launches, keynote-style decks |
| `editorial-infographic` | clean + cool + editorial + dense | journalism, research explainers |
| `fantasy-animation` | organic + vibrant + handwritten + minimal | story, animation, playful education |
| `intuition-machine` | clean + cool + technical + dense | academic and technical briefings |
| `pixel-art` | pixel + vibrant + technical + balanced | gaming, retro, developer culture |
| `scientific` | clean + cool + technical + dense | scientific, medical, academic content |
| `vector-illustration` | clean + vibrant + humanist + balanced | creative, friendly, children's content |
| `vintage` | paper + warm + editorial + balanced | history, heritage, archival topics |

## Auto Selection

Pick the first matching signal, otherwise use `blueprint`.

| Source Signals | Preset |
|----------------|--------|
| tutorial, learn, education, guide, beginner | `sketch-notes` |
| hand-drawn, infographic, diagram, process, onboarding | `hand-drawn-edu` |
| classroom, teaching, school, chalkboard | `chalkboard` |
| architecture, system, data, analysis, technical | `blueprint` |
| executive, minimal, clean, simple | `minimal` |
| SaaS, product, dashboard, metrics | `notion` |
| investor, quarterly, business, corporate | `corporate` |
| launch, marketing, keynote, magazine | `bold-editorial` |
| explainer, journalism, science communication | `editorial-infographic` |
| biology, chemistry, medical, scientific | `scientific` |
| history, heritage, vintage, expedition | `vintage` |
| lifestyle, wellness, travel, artistic | `watercolor` |

## Slide Count Heuristic

| Source Length | Recommended Slides |
|---------------|--------------------|
| < 1000 words | 5-10 |
| 1000-3000 words | 10-18 |
| 3000-5000 words | 15-25 |
| > 5000 words | 20-30, consider splitting |

## STYLE_INSTRUCTIONS Guidance

Every `outline.md` must contain one complete `<STYLE_INSTRUCTIONS>` block. Use this structure:

```text
<STYLE_INSTRUCTIONS>
Design Aesthetic: ...

Background:
  Texture: ...
  Base Color: ...

Typography:
  Headlines: ...
  Body: ...

Color Palette:
  Primary Text: ...
  Background: ...
  Accent 1: ...
  Accent 2: ...

Visual Elements:
  - ...

Density Guidelines:
  - ...

Style Rules:
  Do: ...
  Don't: ...
</STYLE_INSTRUCTIONS>
```

Do not name specific fonts unless a user provided a brand system. Describe font appearance instead.
