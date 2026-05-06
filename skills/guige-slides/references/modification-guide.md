# Modification Guide

Prompt files are the source of truth.

## Edit A Slide

1. Edit `prompts/NN-slide-{slug}.md`.
2. Regenerate that slide image.
3. Re-run:

```bash
python3 skills/guige-slides/scripts/merge_to_pptx.py slide-deck/{topic-slug}
python3 skills/guige-slides/scripts/merge_to_pdf.py slide-deck/{topic-slug}
```

## Add A Slide

1. Add a new prompt file at the intended position.
2. Generate its image.
3. Renumber later `NN-slide-*` prompt and image files.
4. Update `outline.md`.
5. Re-merge PPTX/PDF.

## Delete A Slide

1. Remove the prompt and image.
2. Renumber later slides.
3. Update `outline.md`.
4. Re-merge PPTX/PDF.

Only the numeric prefix should change during renumbering. Keep slugs stable when possible.
