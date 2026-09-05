# CLI Reference

```text
main.ts <markdown-file>
  --output <path>
  --profile web|fragment|wechat|email|bare
  --theme default|simple|grace|modern
  --color <preset|css-name|hex>
  --font-family <preset|safe-css-stack>
  --font-size <14-18>
  --code-theme github|github-dark|dark|monokai|nord|<highlight-name>
  --title <text>
  --allow-html
  --line-number
  --count
  --legend alt|title|alt-title|title-alt|none
  --mac-code-block | --no-mac-code-block
  --keep-title | --remove-title
  --cite | --no-cite
  --base-url <url>
  --css-mode embedded|inline|external|none
  --css-output <path>
  --assets preserve|copy|embed|download
  --asset-dir <path>
  --diagram-format source|svg|png|off
  --diagram-dir <path>
  --mermaid-theme default|forest|dark|neutral|base
  --mermaid-scale <0-4>
  --mermaid-width <px>
  --mermaid-bg white|transparent|<hex>
  --no-diagrams
  --manifest <path>
  --manifest-version 1|2
  --dry-run
  --json
```

Defaults are `web`, `default`, embedded CSS, preserved asset paths, source diagram fallback, retained title, citations off, and manifest schema v2.

When output HTML already exists, it is moved to a timestamped `.bak-*` file before replacement. `--dry-run` performs parsing, validation, and manifest construction without writing output files or invoking diagram renderers.

Named colors include `blue`, `green`, `vermilion`, `yellow`, `purple`, `sky`, `rose`, `olive`, `black`, `gray`, `pink`, `red`, and `orange`. Font presets are `sans`, `serif`, `serif-cjk`, and `mono`.
