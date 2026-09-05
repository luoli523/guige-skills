# Output Profiles

Profiles describe destination constraints; themes describe appearance. Keep these concerns separate.

## Profiles

- `web`: complete HTML5 document with metadata and embedded CSS by default.
- `fragment`: reusable `<article>` fragment with no document wrapper.
- `wechat`: complete document whose body styles are inlined; removes the first H1/H2 and enables citations unless explicitly overridden.
- `email`: complete document with inline styles and conservative markup.
- `bare`: semantic `<article>` fragment with no CSS.

## CSS modes

Override the profile default with `--css-mode`:

- `embedded`: put CSS in a `<style>` element.
- `inline`: inline declarations into rendered elements.
- `external`: write a separate stylesheet and link it from complete documents.
- `none`: emit no presentation CSS.

`--css-output` chooses the external stylesheet path. Relative asset and stylesheet paths are calculated from the HTML output directory.

## Themes

Available themes are `default`, `simple`, `grace`, and `modern`. Customize them with `--color`, `--font-family`, `--font-size`, and `--code-theme`.
