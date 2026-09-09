# Gui Ge Character Reference

`guige-character.png` is the single, version-controlled source image for the
Gui Ge (鬼哥) character. It replaces any personal Downloads-path dependency and
must not be copied into individual skills as a maintained asset.

## Canonical path

From a skill root, use:

```text
../../references/guige-character.png
```

At runtime, a workflow may copy it into its task-local `refs/` directory when
the image backend needs local reference files. The copied file is disposable;
the source of truth remains this directory.

## When to use it

Pass the image as a character/style reference only when the user asks for a
Gui Ge/鬼哥 appearance, narrator, or branded visual. Generic image-generation
skills must not add it implicitly. If a backend cannot accept image references,
use the following traits in the prompt instead:

- Q-style young male narrator with sleepy half-lidded eyes and a mildly
  sarcastic, deadpan expression.
- Orange headband bearing the Chinese text `鬼哥`, blue hoodie, and acoustic
  guitar as signature elements.
- Clean, expressive cartoon silhouette; use the character as a narrator,
  sticker, pointer, or callout host without overpowering the main information.

## Maintenance

Keep the filename stable when replacing the approved reference image. Update
the image and this document together if its visual identity or permitted use
changes.
