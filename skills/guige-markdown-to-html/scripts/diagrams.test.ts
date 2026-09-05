import { describe, expect, test } from "bun:test";
import { mkdtemp, readFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { processDiagrams, type DiagramRenderer } from "./lib/diagrams";
import { renderMarkdown } from "./lib/renderer";

describe("diagram processing", () => {
  test("replaces a diagram source block with a generated static image", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-diagram-"));
    const htmlPath = path.join(root, "article.html");
    const result = renderMarkdown("```mermaid\ngraph TD; A-->B\n```", path.join(root, "article.md"));
    const renderer: DiagramRenderer = async () => ({
      bytes: new TextEncoder().encode("<svg></svg>"),
      mimeType: "image/svg+xml",
    });

    await processDiagrams(result, "svg", htmlPath, "diagrams", false, renderer);

    expect(result.contentHtml).toContain('src="diagrams/mermaid-');
    expect(result.contentHtml).not.toContain("diagram-mermaid");
    expect(result.diagrams[0]).toEqual(expect.objectContaining({ rendered: true, format: "svg" }));
    expect(await readFile(result.diagrams[0]!.outputPath!, "utf8")).toBe("<svg></svg>");
  });

  test("keeps source and records a warning when no renderer is available", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-diagram-fallback-"));
    const result = renderMarkdown("```plantuml\nA -> B\n```", path.join(root, "article.md"));

    await processDiagrams(result, "png", path.join(root, "article.html"), "diagrams", false, async () => null);

    expect(result.contentHtml).toContain("diagram-plantuml");
    expect(result.diagrams[0]!.rendered).toBe(false);
    expect(result.warnings.some((warning) => warning.includes("renderer unavailable"))).toBe(true);
  });

  test("removes diagram blocks when diagrams are disabled", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-diagram-off-"));
    const result = renderMarkdown("Before\n\n```mermaid\ngraph TD; A-->B\n```\n\nAfter", path.join(root, "article.md"));

    await processDiagrams(result, "off", path.join(root, "article.html"));

    expect(result.contentHtml).not.toContain("diagram-mermaid");
    expect(result.contentHtml).toContain("Before");
    expect(result.contentHtml).toContain("After");
  });
});
