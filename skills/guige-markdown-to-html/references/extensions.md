# Markdown Extensions and Assets

## Raw HTML

Raw HTML is escaped by default. `--allow-html` preserves allowlisted structural markup after sanitization. Scripts, event handlers, executable URLs, and unsupported elements remain blocked.

## Math

Use `$...$` for inline math and `$$...$$` for display math. Output uses MathML so general web documents do not depend on a remote JavaScript runtime.

## Alerts and ruby

GitHub-style alerts use blockquotes such as `> [!NOTE]`. Ruby annotations use `{汉字|hàn zì}`.

## Diagrams

Fenced `mermaid` and `plantuml` blocks are preserved as safe source blocks by default.

- `--diagram-format svg|png` requests static rendering through local `mmdc` or `plantuml`.
- `--diagram-format source` keeps source blocks and does not launch an external process.
- `--diagram-format off` or `--no-diagrams` removes diagram blocks.
- Missing renderers or rendering errors produce warnings and retain the source block.
- Mermaid static rendering accepts `--mermaid-theme`, `--mermaid-scale`, `--mermaid-width`, and `--mermaid-bg`.

## Images

Both `![alt](path)` and Obsidian `![[path|alt]]` are supported. Obsidian embeds fall back to the document's `Attachments/` directory when appropriate.

- `preserve`: retain source paths; no I/O.
- `copy`: copy local files beside the HTML under `assets/` or `--asset-dir`.
- `embed`: turn local or explicitly fetched raster images into Data URIs.
- `download`: explicitly fetch HTTP(S) raster images and copy local images.

Remote downloads reject private-network URLs, redirections to private networks, SVG responses, non-image content, and payloads over 20 MiB.
