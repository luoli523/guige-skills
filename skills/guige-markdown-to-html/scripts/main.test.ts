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

describe("wechat inline style coverage", () => {
  const listArticle = [
    "Lead **FACT** note.",
    "- First **待核** item\n- Second item",
    "1. Step one\n2. Step two",
    "| 信号 | 标签 |\n|---|---|\n| Harness | **FACT** |",
  ].join("\n\n");

  test("inlines styles on the elements wechat would otherwise leave bare", () => {
    const result = renderMarkdown(listArticle, sourcePath, { profile: "wechat" });

    for (const tag of ["strong", "li", "ul", "ol", "p", "td", "th"]) {
      const opens = result.contentHtml.match(new RegExp(`<${tag}(\\s[^>]*)?>`, "g")) ?? [];
      expect(opens.length).toBeGreaterThan(0);
      expect(opens.every((open) => open.includes("style="))).toBe(true);
    }
    expect(result.contentHtml).toMatch(/<td style="[^"]*word-break:\s*keep-all/);
  });

  test("keeps the wechat supplement out of the other profiles", () => {
    const wechat = renderMarkdown(listArticle, sourcePath, { profile: "wechat" });
    const web = renderMarkdown(listArticle, sourcePath, { profile: "web", cssMode: "inline" });

    expect(wechat.contentHtml).toMatch(/<strong style="[^"]*color:/);
    expect(web.contentHtml).toContain("<strong>");
    expect(web.contentHtml).not.toContain("letter-spacing");
    expect(web.contentHtml).not.toContain("keep-all");
  });

  test("renders references as plain text for wechat and as links elsewhere", () => {
    const article = "See [Harness](https://example.com/harness) today.";
    const wechat = renderMarkdown(article, sourcePath, { profile: "wechat" });
    const web = renderMarkdown(article, sourcePath, { profile: "web", cite: true });

    const wechatReferences = wechat.contentHtml.slice(wechat.contentHtml.indexOf("参考链接"));
    expect(wechatReferences).not.toContain("<a href");
    expect(wechatReferences).toContain("[1] Harness: https://example.com/harness");

    const webReferences = web.contentHtml.slice(web.contentHtml.indexOf("参考链接"));
    expect(webReferences).toContain('<a href="https://example.com/harness"');
  });

  test("suppresses the ordered-list marker so the [n] label is not numbered twice", () => {
    const result = renderMarkdown("See [Doc](https://example.com/doc).", sourcePath, { profile: "wechat" });

    expect(result.contentHtml).toMatch(/<ol style="[^"]*list-style:\s*none/);
  });

  test("takes the citation label from the link text, including nested markup", () => {
    const result = renderMarkdown(
      "A [**bold**text](https://example.com/a) and B [`pkg==1.0`](https://example.com/b).",
      sourcePath,
      { profile: "wechat" },
    );

    expect(result.contentHtml).toContain("[1] boldtext: https://example.com/a");
    expect(result.contentHtml).toContain("[2] pkg==1.0: https://example.com/b");
  });

  test("does not repeat the url when an autolink is its own label", () => {
    const result = renderMarkdown("Bare <https://example.com/page> here.", sourcePath, { profile: "wechat" });

    expect(result.contentHtml).toContain("[1] https://example.com/page");
    expect(result.contentHtml).not.toContain("https://example.com/page: https://example.com/page");
  });

  test("applies the resolved color to both the heading block and emphasis", () => {
    const result = renderMarkdown("## Section\n\n**FACT** claim.", sourcePath, {
      profile: "wechat",
      keepTitle: true,
      color: "green",
    });

    const accent = result.css.match(/\.markdown-body a\{color:(#[0-9a-f]{3,8})/i)?.[1];
    expect(accent).toBeTruthy();
    expect(result.contentHtml).toContain(`background: ${accent}`);
    expect(result.contentHtml).toMatch(new RegExp(`<strong style="color: ${accent}`, "i"));
  });

  test("wechat headings win over the selected theme", () => {
    const result = renderMarkdown("## Section\n\nBody", sourcePath, {
      profile: "wechat",
      keepTitle: true,
      theme: "modern",
    });

    const heading = result.contentHtml.match(/<h2[^>]*>/)![0];
    expect(heading).toContain("display: table");
    expect(heading).toContain("border-bottom: none");
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
