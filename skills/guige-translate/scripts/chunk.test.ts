import { afterEach, describe, expect, test } from "bun:test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { chunkMarkdownFile } from "./chunk";

const tempDirs: string[] = [];

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("Markdown chunking", () => {
  test("preserves frontmatter separately and splits at section boundaries", () => {
    const dir = mkdtempSync(join(tmpdir(), "guige-translate-"));
    tempDirs.push(dir);
    const source = join(dir, "source.md");
    const output = join(dir, "output");
    writeFileSync(
      source,
      [
        "---",
        "title: Example",
        "---",
        "",
        "# First",
        "alpha beta gamma",
        "",
        "# Second",
        "delta epsilon zeta",
      ].join("\n"),
    );

    const result = chunkMarkdownFile(source, { maxWords: 5, outputDir: output });

    expect(result.frontmatter).toBe(true);
    expect(result.chunks).toBe(2);
    expect(readFileSync(join(output, "chunks", "frontmatter.md"), "utf8")).toBe(
      "---\ntitle: Example\n---",
    );
    expect(readFileSync(join(output, "chunks", "chunk-01.md"), "utf8")).toContain(
      "# First",
    );
    expect(readFileSync(join(output, "chunks", "chunk-02.md"), "utf8")).toContain(
      "# Second",
    );
  });

  test("counts CJK characters and Latin words toward the chunk limit", () => {
    const dir = mkdtempSync(join(tmpdir(), "guige-translate-"));
    tempDirs.push(dir);
    const source = join(dir, "mixed.md");
    writeFileSync(source, "# 标题\n\n你好 world\n\n再见 codex\n");

    const result = chunkMarkdownFile(source, { maxWords: 4 });

    expect(result.chunks).toBeGreaterThan(1);
    expect(result.words_per_chunk.every((count) => count <= 4)).toBe(true);
  });
});
