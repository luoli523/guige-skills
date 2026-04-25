# OpenAI Provider

`guige-imagen` uses the OpenAI Images API through direct HTTPS requests.

## Environment

```dotenv
OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-1.5
OPENAI_BASE_URL=https://api.openai.com/v1
```

`OPENAI_BASE_URL` is optional.

These provider values should live in `.guige-skills/.env`. Ambient shell provider env is ignored unless `GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1` is set.

## Behavior

- Text-to-image uses `POST /images/generations`.
- Reference-image workflows use `POST /images/edits`.
- GPT Image responses are expected to contain base64 image data.
- DALL-E generation requests add `response_format: b64_json`.
- `--quality 2k` maps to OpenAI `high` for GPT Image models and `hd` for DALL-E 3.
- `--quality normal` maps to `medium` for GPT Image models and `standard` for DALL-E 3.

## Size Mapping

When `--size` is not supplied:

| Aspect | GPT Image | DALL-E 3 |
|--------|-----------|----------|
| square | `1024x1024` | `1024x1024` |
| landscape | `1536x1024` | `1792x1024` |
| portrait | `1024x1536` | `1024x1792` |

`gpt-image-2` is also accepted when explicitly configured; for that model, `guige-imagen` mirrors the dynamic aspect-ratio sizing constraints used by the reference skill.
