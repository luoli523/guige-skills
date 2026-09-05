# Manifest Contracts

## General schema v2

Use v2 for new integrations. It records the input and output paths, output mode, profile, theme, CSS mode, normalized metadata, processed assets, diagrams, document statistics, and warnings.

```json
{
  "schemaVersion": 2,
  "inputPath": "/path/article.md",
  "htmlPath": "/path/article.html",
  "outputMode": "document",
  "profile": "web",
  "theme": "default",
  "cssMode": "embedded",
  "metadata": {
    "title": "Article",
    "author": "Author",
    "summary": "Summary",
    "language": "en",
    "canonicalUrl": "https://example.com/article",
    "cover": "cover.png",
    "slug": "article"
  },
  "assets": [],
  "diagrams": [],
  "warnings": [],
  "stats": { "words": 100, "characters": 600, "readingMinutes": 1 }
}
```

## Legacy schema v1

Schema v1 exists only for `guige-to-wechat`. Generate it explicitly:

```bash
bun scripts/main.ts article.md --profile wechat \
  --manifest article.wechat.json --manifest-version 1
```

It retains `htmlPath`, `assetBaseDir`, `title`, `summary`, `author`, `contentSourceUrl`, `cover`, and `contentImages`.
