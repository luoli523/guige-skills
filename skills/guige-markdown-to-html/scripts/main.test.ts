import { describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { buildManifest, renderMarkdown } from "./lib/renderer";

const sourcePath = path.resolve("/tmp/guige-markdown-to-html/article.md");

describe("generic rendering profiles", () => {
  test("web is the generic default with a complete document and embedded CSS", () => {
    const result = renderMarkdown("# Hello\n\nA **portable** document.", sourcePath);

    expect(result.profile).toBe("web");
    expect(result.html).toStartWith("<!doctype html>");
    expect(result.html).toContain("<style>");
    expect(result.html).toContain("<h1>Hello</h1>");
    expect(result.html).toContain("<strong>portable</strong>");
  });

  test("fragment emits reusable content without a document wrapper", () => {
    const result = renderMarkdown("## Section\n\nBody", sourcePath, { profile: "fragment" });

    expect(result.html).toBe(result.contentHtml);
    expect(result.html).not.toContain("<!doctype html>");
    expect(result.html).not.toContain("<style>");
  });

  test("supports inline and unstyled CSS modes independently of the profile", () => {
    const inline = renderMarkdown("# Inline", sourcePath, { cssMode: "inline" });
    const none = renderMarkdown("# Plain", sourcePath, { cssMode: "none" });

    expect(inline.contentHtml).toContain("style=");
    expect(inline.html).not.toContain("<style>");
    expect(none.html).not.toContain("<style>");
    expect(none.contentHtml).not.toContain("style=");
  });

  test("wechat preserves legacy inline styling and title removal", () => {
    const result = renderMarkdown(
      "# Title\n\nRead [source](https://example.com).",
      sourcePath,
      { profile: "wechat" },
    );

    expect(result.contentHtml).not.toContain("<h1");
    expect(result.contentHtml).toContain("style=");
    expect(result.contentHtml).toContain("<sup>[1]</sup>");
    expect(result.contentHtml).toContain("参考链接");
  });

  test("wechat preserves the legacy lead callout and can disable it", () => {
    const withLead = renderMarkdown(
      "---\ndescription: Summary lead\nhighlight: Important **idea**\n---\n\n# Title\n\nBody",
      sourcePath,
      { profile: "wechat" },
    );
    const withoutLead = renderMarkdown(
      "---\ndescription: Summary lead\nhighlight: false\n---\n\n# Title\n\nBody",
      sourcePath,
      { profile: "wechat" },
    );

    expect(withLead.contentHtml).toContain('class="lead-callout"');
    expect(withLead.contentHtml).toContain("<strong");
    expect(withoutLead.contentHtml).not.toContain('class="lead-callout"');
  });
});

describe("markdown and safety", () => {
  test("renders GFM tables, task lists, strikethrough, and footnotes", () => {
    const markdown = [
      "~~old~~",
      "",
      "- [x] shipped",
      "",
      "| A | B |",
      "| - | - |",
      "| 1 | 2 |",
      "",
      "Statement[^1]",
      "",
      "[^1]: Evidence",
    ].join("\n");

    const result = renderMarkdown(markdown, sourcePath);

    expect(result.contentHtml).toContain("<s>old</s>");
    expect(result.contentHtml).toContain('type="checkbox"');
    expect(result.contentHtml).toContain("<table>");
    expect(result.contentHtml).toContain("footnote-ref");
  });

  test("renders alerts, ruby annotations, and math", () => {
    const markdown = [
      "> [!NOTE]",
      "> Portable alert",
      "",
      "Read {汉字|hàn zì} and calculate $E=mc^2$.",
    ].join("\n");

    const result = renderMarkdown(markdown, sourcePath);

    expect(result.contentHtml).toContain("markdown-alert-note");
    expect(result.contentHtml).toContain("<ruby>汉字<rt>hàn zì</rt></ruby>");
    expect(result.contentHtml).toContain("katex");
    expect(result.contentHtml).toContain("E=mc");
  });

  test("preserves complex MathML structures", () => {
    const result = renderMarkdown("$$\\sqrt{\\frac{1}{2}} + \\begin{matrix}a&b\\\\c&d\\end{matrix}$$", sourcePath);

    expect(result.contentHtml).toContain("<msqrt>");
    expect(result.contentHtml).toContain("<mfrac>");
    expect(result.contentHtml).toContain("<mtable");
  });

  test("preserves Mermaid and PlantUML as safe diagram fallbacks", () => {
    const markdown = [
      "```mermaid",
      "graph TD; A-->B",
      "```",
      "",
      "```plantuml",
      "Alice -> Bob: hello",
      "```",
    ].join("\n");

    const result = renderMarkdown(markdown, sourcePath);

    expect(result.contentHtml).toContain('class="diagram diagram-mermaid"');
    expect(result.contentHtml).toContain('class="diagram diagram-plantuml"');
    expect(result.diagrams).toHaveLength(2);
    expect(result.warnings).toHaveLength(2);
  });

  test("resolves Obsidian image embeds from the document and Attachments directory", () => {
    const root = mkdtempSync(path.join(os.tmpdir(), "guige-md-html-obsidian-"));
    mkdirSync(path.join(root, "Attachments"));
    writeFileSync(path.join(root, "local.png"), "local");
    writeFileSync(path.join(root, "Attachments", "fallback.webp"), "fallback");

    const result = renderMarkdown(
      "![[local.png]]\n\n![[fallback.webp|Fallback alt]]",
      path.join(root, "article.md"),
    );

    expect(result.contentHtml).toContain('src="local.png"');
    expect(result.contentHtml).toContain('src="Attachments/fallback.webp"');
    expect(result.contentHtml).toContain('alt="Fallback alt"');
    expect(result.assets.map((asset) => asset.resolvedPath)).toEqual([
      path.join(root, "local.png"),
      path.join(root, "Attachments", "fallback.webp"),
    ]);
  });

  test("does not execute raw HTML or javascript URLs by default", () => {
    const result = renderMarkdown(
      '<script>alert(1)</script>\n\n[unsafe](javascript:alert(1))\n\n<img src=x onerror="alert(2)">',
      sourcePath,
    );

    expect(result.html).not.toContain("<script>");
    expect(result.html).not.toContain('href="javascript:');
    expect(result.html).not.toContain("<img src=x");
  });

  test("can preserve safe raw HTML while stripping executable content", () => {
    const result = renderMarkdown(
      '<div class="callout" onclick="alert(1)">Safe</div><script>alert(2)</script>',
      sourcePath,
      { allowHtml: true },
    );

    expect(result.contentHtml).toContain('<div class="callout">Safe</div>');
    expect(result.contentHtml).not.toContain("onclick");
    expect(result.contentHtml).not.toContain("<script>");
  });

  test("allows image data URIs but strips executable data links", () => {
    const result = renderMarkdown(
      '<a href="data:text/html,<script>alert(1)</script>">unsafe</a><img src="data:image/png;base64,iVBORw==">',
      sourcePath,
      { allowHtml: true },
    );

    expect(result.contentHtml).not.toContain('href="data:');
    expect(result.contentHtml).toContain('src="data:image/png;base64,iVBORw=="');
  });

  test("rejects CSS injection through color and font options", () => {
    expect(() => renderMarkdown("Text", sourcePath, { color: "red;}body{display:none" }))
      .toThrow("color");
    expect(() => renderMarkdown("Text", sourcePath, { fontFamily: "sans-serif; background:url(x)" }))
      .toThrow("font family");
  });

  test("supports title override, code line numbers, and document statistics", () => {
    const result = renderMarkdown(
      "# Original\n\n```ts\nconst first = 1;\nconst second = 2;\n```\n\n中文 text",
      sourcePath,
      { title: "Override", lineNumbers: true, count: true },
    );

    expect(result.metadata.title).toBe("Override");
    expect(result.html).toContain("<title>Override</title>");
    expect(result.contentHtml).toContain('class="code-line" data-line="1"');
    expect(result.contentHtml).toContain('class="document-stats"');
    expect(result.stats.words).toBeGreaterThan(0);
    expect(result.stats.readingMinutes).toBeGreaterThanOrEqual(1);
  });

  test("renders configurable image captions", () => {
    const result = renderMarkdown(
      '![Architecture](diagram.png "System overview")',
      sourcePath,
      { legend: "alt-title" },
    );

    expect(result.contentHtml).toContain('class="image-caption"');
    expect(result.contentHtml).toContain("Architecture — System overview");
  });

  test("uses Mac-style code headers only when enabled", () => {
    const enabled = renderMarkdown("```js\nconst x = 1\n```", sourcePath, { macCodeBlock: true });
    const disabled = renderMarkdown("```js\nconst x = 1\n```", sourcePath, { macCodeBlock: false });

    expect(enabled.contentHtml).toContain('class="mac-code-header"');
    expect(disabled.contentHtml).not.toContain('class="mac-code-header"');
  });

  test("ships visible syntax colors for light and dark code themes", () => {
    const light = renderMarkdown("```js\nconst x = 1\n```", sourcePath, { codeTheme: "github" });
    const dark = renderMarkdown("```js\nconst x = 1\n```", sourcePath, { codeTheme: "nord" });

    expect(light.contentHtml).toContain('class="hljs language-js"');
    expect(light.css).toContain(".hljs-keyword");
    expect(dark.css).toContain("background:#2e3440");
  });
});

describe("manifest compatibility", () => {
  test("builds generic schema v2 and legacy publisher schema v1", () => {
    const markdown = [
      "---",
      "title: Manifest Test",
      "author: Gui Ge",
      "description: Portable output",
      "image: cover.webp",
      "slug: manifest-test",
      "---",
      "",
      "![Chart](imgs/chart.png)",
    ].join("\n");
    const result = renderMarkdown(markdown, sourcePath);

    const generic = buildManifest(result, sourcePath, "/tmp/article.html", 2);
    expect(generic.schemaVersion).toBe(2);
    expect(generic.profile).toBe("web");
    expect(generic.metadata).toEqual(expect.objectContaining({ title: "Manifest Test" }));
    expect(generic.assets).toHaveLength(1);

    const legacy = buildManifest(result, sourcePath, "/tmp/article.html", 1);
    expect(legacy.schemaVersion).toBe(1);
    expect(legacy.contentSourceUrl).toBe("https://luoli523.github.io/p/manifest-test/");
    expect(legacy.cover).toEqual(expect.objectContaining({ source: "cover.webp" }));
    expect(legacy.contentImages).toHaveLength(1);
  });

  test("legacy manifest recognizes lowercase Hugo cover fields", () => {
    const result = renderMarkdown(
      "---\ntitle: Cover\ncoverimage: lower.webp\n---\n\nBody",
      sourcePath,
    );

    expect(buildManifest(result, sourcePath, "/tmp/article.html", 1).cover)
      .toEqual(expect.objectContaining({ source: "lower.webp" }));
  });
});
