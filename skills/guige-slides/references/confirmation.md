# Confirmation Copy

Use concise questions. Batch them when the runtime supports multi-question input.

## Initial Confirmation

Ask:

- Style: recommended preset, one alternative preset, or custom dimensions.
- Audience: general, beginners, experts, executives.
- Slide count: recommended, fewer, more.
- Outline review: yes/no.
- Prompt review: yes/no.

Recommended defaults:

```text
style={recommended_preset}
audience=general
slides={recommended_count}
review-outline=yes
review-prompts=yes
```

If the user says `--no-confirm` or equivalent, state the assumed choices in a progress update before generating.

## Existing Deck

If `slide-deck/{topic-slug}/` already contains output, ask:

```text
Existing deck found. Choose one:
1. Regenerate outline only
2. Regenerate images from existing prompts
3. Backup folder and regenerate all
4. Exit
```

## Outline Review

```text
Ready to generate prompts?
1. Proceed
2. I will edit outline.md first
3. Regenerate outline
```

## Prompt Review

```text
Ready to generate slide images?
1. Proceed
2. I will edit prompts first
3. Regenerate prompts
```
