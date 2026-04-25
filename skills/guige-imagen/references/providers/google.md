# Google Provider

`guige-imagen` uses the Gemini API REST surface through direct HTTPS requests.

## Environment

```dotenv
GOOGLE_API_KEY=...
GEMINI_API_KEY=...          # accepted alias
GOOGLE_IMAGE_MODEL=gemini-3-pro-image-preview
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
```

`GOOGLE_BASE_URL` is optional.

## Gemini Models

Gemini image models use:

```text
POST /v1beta/models/{model}:generateContent
```

The request includes text parts, optional inline reference images, and `generationConfig.responseModalities`.

Use Gemini models when you need `--ref`.

## Imagen Models

Imagen models use:

```text
POST /v1beta/models/{model}:predict
```

The request includes `instances[].prompt` and `parameters` such as `sampleCount`, `aspectRatio`, and `imageSize`.

Imagen does not support `--ref` in this skill.
