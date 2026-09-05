import { describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, readFile, stat, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { parseCliArgs, runCli } from "./main";

describe("CLI contract", () => {
  test("parses the generic output contract", () => {
    const options = parseCliArgs([
      "article.md",
      "--profile", "fragment",
      "--theme", "modern",
      "--assets", "preserve",
      "--manifest-version", "2",
      "--no-cite",
      "--keep-title",
      "--title", "Override",
      "--allow-html",
      "--line-number",
      "--count",
      "--legend", "alt",
      "--mac-code-block",
      "--diagram-format", "source",
      "--mermaid-theme", "forest",
      "--mermaid-scale", "2",
      "--mermaid-width", "860",
      "--mermaid-bg", "transparent",
    ]);

    expect(options).toEqual(expect.objectContaining({
      inputPath: "article.md",
      profile: "fragment",
      theme: "modern",
      assetMode: "preserve",
      manifestVersion: 2,
      cite: false,
      keepTitle: true,
      title: "Override",
      allowHtml: true,
      lineNumbers: true,
      count: true,
      legend: "alt",
      macCodeBlock: true,
      diagramFormat: "source",
      mermaidTheme: "forest",
      mermaidScale: 2,
      mermaidWidth: 860,
      mermaidBackground: "transparent",
    }));
  });

  test("writes HTML and a generic manifest to caller-selected paths", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "dist", "article.html");
    const manifest = path.join(root, "dist", "article.json");
    await writeFile(input, "# Portable\n\nHello.", "utf8");

    const result = await runCli([
      input,
      "--output", output,
      "--manifest", manifest,
      "--manifest-version", "2",
      "--json",
    ]);

    expect(result.success).toBe(true);
    expect(result.schemaVersion).toBe(2);
    expect(await readFile(output, "utf8")).toContain("<!doctype html>");
    expect(JSON.parse(await readFile(manifest, "utf8")).profile).toBe("web");
  });

  test("backs up an existing output before replacement", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-backup-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "article.html");
    await writeFile(input, "# New", "utf8");
    await writeFile(output, "old content", "utf8");

    const result = await runCli([input, "--output", output]);

    expect(result.backupPath).toBeString();
    expect(await readFile(result.backupPath!, "utf8")).toBe("old content");
    expect(await readFile(output, "utf8")).toContain("New");
  });

  test("refuses output paths that would overwrite an input or another artifact", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-collision-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "article.html");
    await writeFile(input, "# Keep me", "utf8");

    await expect(runCli([input, "--output", input])).rejects.toThrow("must differ from the input");
    await expect(runCli([input, "--output", output, "--manifest", output])).rejects.toThrow("manifest path must differ");
    await expect(runCli([
      input,
      "--output", output,
      "--css-mode", "external",
      "--css-output", output,
    ])).rejects.toThrow("stylesheet path must differ");
    expect(await readFile(input, "utf8")).toBe("# Keep me");
  });

  test("dry-run validates without writing output or manifest", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-dry-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "article.html");
    const manifest = path.join(root, "article.json");
    await writeFile(input, "# Dry", "utf8");

    const result = await runCli([
      input,
      "--output", output,
      "--manifest", manifest,
      "--dry-run",
    ]);

    expect(result.dryRun).toBe(true);
    await expect(stat(output)).rejects.toThrow();
    await expect(stat(manifest)).rejects.toThrow();
  });

  test("dry-run does not fetch remote images", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-dry-download-"));
    const input = path.join(root, "article.md");
    await writeFile(input, "![Remote](https://cdn.example.test/pixel.png)", "utf8");
    const originalFetch = globalThis.fetch;
    let fetched = false;
    globalThis.fetch = (async () => {
      fetched = true;
      throw new Error("network should not be called");
    }) as unknown as typeof fetch;
    try {
      const result = await runCli([input, "--assets", "download", "--dry-run"]);
      expect((result.warnings as string[]).some((warning) => warning.includes("dry-run"))).toBe(true);
    } finally {
      globalThis.fetch = originalFetch;
    }
    expect(fetched).toBe(false);
  });

  test("can still emit schema v1 for guige-to-wechat", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-v1-"));
    const input = path.join(root, "article.md");
    const manifest = path.join(root, "article.wechat.json");
    await writeFile(input, "---\ntitle: Legacy\n---\n\n# Legacy", "utf8");

    const result = await runCli([
      input,
      "--profile", "wechat",
      "--manifest", manifest,
      "--manifest-version", "1",
    ]);

    expect(result.schemaVersion).toBe(1);
    expect(JSON.parse(await readFile(manifest, "utf8")).title).toBe("Legacy");
  });

  test("copies local images into a selected asset directory and rewrites HTML", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-copy-"));
    const input = path.join(root, "article.md");
    const image = path.join(root, "pixel.png");
    const output = path.join(root, "dist", "article.html");
    await writeFile(input, "![Pixel](pixel.png)", "utf8");
    await writeFile(image, new Uint8Array([0x89, 0x50, 0x4e, 0x47]));

    const result = await runCli([
      input,
      "--output", output,
      "--assets", "copy",
      "--asset-dir", "assets",
    ]);

    expect(await readFile(path.join(root, "dist", "assets", "pixel.png"))).toHaveLength(4);
    expect(await readFile(output, "utf8")).toContain('src="assets/pixel.png"');
    expect((result.assets as Array<{ outputPath: string }>)[0]!.outputPath)
      .toBe(path.join(root, "dist", "assets", "pixel.png"));
  });

  test("does not copy an image onto itself", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-same-asset-"));
    const assets = path.join(root, "assets");
    await mkdir(assets);
    await writeFile(path.join(assets, "pixel.png"), new Uint8Array([0x89, 0x50, 0x4e, 0x47]));
    const input = path.join(root, "article.md");
    await writeFile(input, "![Pixel](assets/pixel.png)", "utf8");

    await runCli([input, "--assets", "copy"]);

    expect(await readFile(path.join(assets, "pixel.png"))).toHaveLength(4);
  });

  test("embeds local images for a portable single-file document", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-embed-"));
    const input = path.join(root, "article.md");
    const image = path.join(root, "pixel.png");
    const output = path.join(root, "article.html");
    await writeFile(input, "![Pixel](pixel.png)", "utf8");
    await writeFile(image, new Uint8Array([0x89, 0x50, 0x4e, 0x47]));

    await runCli([input, "--output", output, "--assets", "embed"]);

    expect(await readFile(output, "utf8")).toContain('src="data:image/png;base64,iVBORw=="');
  });

  test("downloads an explicitly requested remote raster image", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-download-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "article.html");
    await writeFile(input, "![Remote](https://cdn.example.test/pixel.png)", "utf8");
    const originalFetch = globalThis.fetch;
    globalThis.fetch = (async () => new Response(
      new Uint8Array([0x89, 0x50, 0x4e, 0x47]),
      { status: 200, headers: { "content-type": "image/png" } },
    )) as unknown as typeof fetch;
    try {
      await runCli([input, "--output", output, "--assets", "download"]);
    } finally {
      globalThis.fetch = originalFetch;
    }

    expect(await readFile(path.join(root, "assets", "pixel.png"))).toHaveLength(4);
    expect(await readFile(output, "utf8")).toContain('src="assets/pixel.png"');
  });

  test("adds an extension to downloaded images using their MIME type", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-download-extension-"));
    const input = path.join(root, "article.md");
    await writeFile(input, "![Remote](https://cdn.example.test/image)", "utf8");
    const originalFetch = globalThis.fetch;
    globalThis.fetch = (async () => new Response(
      new Uint8Array([0x89, 0x50, 0x4e, 0x47]),
      { status: 200, headers: { "content-type": "image/png" } },
    )) as unknown as typeof fetch;
    try {
      await runCli([input, "--assets", "download"]);
    } finally {
      globalThis.fetch = originalFetch;
    }

    expect(await readFile(path.join(root, "assets", "image.png"))).toHaveLength(4);
  });

  test("rejects a remote image that resolves or redirects to a private network", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-private-"));
    const input = path.join(root, "article.md");
    await writeFile(input, "![Remote](https://cdn.example.test/pixel.png)", "utf8");
    const response = new Response(
      new Uint8Array([0x89, 0x50, 0x4e, 0x47]),
      { status: 200, headers: { "content-type": "image/png" } },
    );
    Object.defineProperty(response, "url", { value: "http://127.0.0.1/internal.png" });
    const originalFetch = globalThis.fetch;
    globalThis.fetch = (async () => response) as unknown as typeof fetch;
    try {
      await expect(runCli([input, "--assets", "download"]))
        .rejects.toThrow("private network");
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  test("writes an external stylesheet when requested", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "guige-md-html-css-"));
    const input = path.join(root, "article.md");
    const output = path.join(root, "dist", "article.html");
    const cssOutput = path.join(root, "dist", "article.css");
    await writeFile(input, "# Styled", "utf8");

    await runCli([
      input,
      "--output", output,
      "--css-mode", "external",
      "--css-output", cssOutput,
    ]);

    expect(await readFile(output, "utf8")).toContain('<link rel="stylesheet" href="article.css">');
    expect(await readFile(output, "utf8")).not.toContain("<style>");
    expect(await readFile(cssOutput, "utf8")).toContain(".markdown-body");
  });
});
