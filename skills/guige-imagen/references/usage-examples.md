# Usage Examples

## Minimal

```bash
python3 skills/guige-imagen/scripts/main.py \
  --prompt "A clean product photo of a translucent mechanical keyboard"
```

Provider is auto-detected from API keys in `.guige-skills/.env`. Google is preferred when both Google and OpenAI keys are present; pass `--provider` when you need deterministic routing.

If no guige-scoped API key is configured, this CLI cannot generate images by itself. In Codex, use the built-in imagen/image generation tool first; outside Codex, try the current runtime's native image generation tool before reporting the prepared prompt.

Final images are saved to:

```text
~/Downloads/guige-skill-imagen/
```

The filename is derived from the prompt or first Markdown heading in the prompt files.

Ambient shell provider keys are ignored by default. Set `GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1` only when you deliberately want the CLI to use already-exported provider values.

## OpenAI

```bash
python3 skills/guige-imagen/scripts/main.py \
  --provider openai \
  --model gpt-image-1.5 \
  --prompt "A precise technical diagram of a Python CLI pipeline" \
  --ar 16:9 \
  --quality 2k \
  --image openai-diagram.png
```

Reference-image edit:

```bash
python3 skills/guige-imagen/scripts/main.py \
  --provider openai \
  --model gpt-image-1.5 \
  --prompt "Keep the composition, convert it into a clean editorial illustration" \
  --ref refs/source.png \
  --image openai-edit.png
```

## Google Gemini

```bash
python3 skills/guige-imagen/scripts/main.py \
  --provider google \
  --model gemini-3-pro-image-preview \
  --prompt "A compact visual explanation of agentic workflow orchestration" \
  --ar 16:9 \
  --imageSize 2K \
  --image google-gemini.png
```

Reference-image generation:

```bash
python3 skills/guige-imagen/scripts/main.py \
  --provider google \
  --model gemini-3-pro-image-preview \
  --prompt "Use the reference as character style and draw a friendly CLI mascot" \
  --ref refs/style.png \
  --image google-ref.png
```

## Google Imagen

```bash
python3 skills/guige-imagen/scripts/main.py \
  --provider google \
  --model imagen-4.0-generate-001 \
  --prompt "A studio product photo of a matte black fountain pen" \
  --ar 1:1 \
  --image imagen-pen.png
```

Imagen does not support `--ref` in this skill.

## Prompt Files

```bash
python3 skills/guige-imagen/scripts/main.py \
  --promptfiles prompts/system.md prompts/image.md \
  --provider google
```
