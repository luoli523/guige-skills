import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import type { DiagramAsset, RenderResult } from "./renderer";

export type DiagramFormat = "source" | "svg" | "png" | "off";
export interface DiagramRenderOptions {
  mermaidTheme: "default" | "forest" | "dark" | "neutral" | "base";
  mermaidScale: number;
  mermaidWidth: number;
  mermaidBackground: string;
}
export type DiagramRenderer = (
  diagram: DiagramAsset,
  format: "svg" | "png",
  options?: DiagramRenderOptions,
) => Promise<{ bytes: Uint8Array; mimeType: string } | null>;

async function systemDiagramRenderer(
  diagram: DiagramAsset,
  format: "svg" | "png",
  options: DiagramRenderOptions = {
    mermaidTheme: "default",
    mermaidScale: 2,
    mermaidWidth: 860,
    mermaidBackground: "transparent",
  },
): Promise<{ bytes: Uint8Array; mimeType: string } | null> {
  try {
    if (diagram.type === "plantuml") {
      const process = Bun.spawn(["plantuml", `-t${format}`, "-pipe"], {
        stdin: new Blob([diagram.source]),
        stdout: "pipe",
        stderr: "pipe",
      });
      if (await process.exited !== 0) return null;
      return {
        bytes: new Uint8Array(await new Response(process.stdout).arrayBuffer()),
        mimeType: format === "svg" ? "image/svg+xml" : "image/png",
      };
    }
    const temporaryDirectory = await mkdtemp(path.join(os.tmpdir(), "guige-mermaid-"));
    const inputPath = path.join(temporaryDirectory, "diagram.mmd");
    const outputPath = path.join(temporaryDirectory, `diagram.${format}`);
    try {
      await writeFile(inputPath, diagram.source, "utf8");
      const process = Bun.spawn([
        "mmdc", "-i", inputPath, "-o", outputPath,
        "-t", options.mermaidTheme,
        "-s", String(options.mermaidScale),
        "-w", String(options.mermaidWidth),
        "-b", options.mermaidBackground,
      ], {
        stdout: "ignore",
        stderr: "pipe",
      });
      if (await process.exited !== 0) return null;
      return {
        bytes: new Uint8Array(await readFile(outputPath)),
        mimeType: format === "svg" ? "image/svg+xml" : "image/png",
      };
    } finally {
      await rm(temporaryDirectory, { recursive: true, force: true });
    }
  } catch (error) {
    const code = error && typeof error === "object" && "code" in error ? String(error.code) : "";
    if (code === "ENOENT") return null;
    return null;
  }
}

function replaceDiagramBlock(result: RenderResult, type: DiagramAsset["type"], replacement: string): void {
  const pattern = new RegExp(
    `<pre class="diagram diagram-${type}"[^>]*><code>[\\s\\S]*?<\\/code><\\/pre>\\n?`,
  );
  result.contentHtml = result.contentHtml.replace(pattern, replacement);
  result.html = result.html.replace(pattern, replacement);
}

export async function processDiagrams(
  result: RenderResult,
  format: DiagramFormat,
  htmlPath: string,
  diagramDirectory = "diagrams",
  dryRun = false,
  renderer: DiagramRenderer = systemDiagramRenderer,
  renderOptions: DiagramRenderOptions = {
    mermaidTheme: "default",
    mermaidScale: 2,
    mermaidWidth: 860,
    mermaidBackground: "transparent",
  },
): Promise<RenderResult> {
  result.warnings = result.warnings.filter((warning) => !warning.includes("diagram kept as source"));
  if (format === "source") {
    result.warnings.push(...result.diagrams.map((diagram) => `${diagram.type} diagram kept as source`));
    return result;
  }
  if (format === "off") {
    for (const diagram of result.diagrams) replaceDiagramBlock(result, diagram.type, "");
    return result;
  }
  const outputDirectory = path.isAbsolute(diagramDirectory)
    ? diagramDirectory
    : path.resolve(path.dirname(htmlPath), diagramDirectory);
  for (const diagram of result.diagrams) {
    if (dryRun) {
      result.warnings.push(`${diagram.type} diagram not rendered during dry-run`);
      continue;
    }
    const rendered = await renderer(diagram, format, renderOptions);
    if (!rendered) {
      result.warnings.push(`${diagram.type} renderer unavailable; diagram kept as source`);
      continue;
    }
    const hash = createHash("sha256").update(`${diagram.type}\0${format}\0${diagram.source}`).digest("hex").slice(0, 12);
    const filename = `${diagram.type}-${hash}.${format}`;
    const outputPath = path.join(outputDirectory, filename);
    await mkdir(outputDirectory, { recursive: true });
    await writeFile(outputPath, rendered.bytes);
    const relativePath = path.relative(path.dirname(htmlPath), outputPath).split(path.sep).join("/");
    const imageHtml = `<img src="${relativePath}" alt="${diagram.type} diagram">`;
    replaceDiagramBlock(result, diagram.type, imageHtml);
    diagram.rendered = true;
    diagram.format = format;
    diagram.outputPath = outputPath;
    diagram.mimeType = rendered.mimeType;
    result.assets.push({
      type: "image",
      source: relativePath,
      resolvedPath: outputPath,
      outputPath,
      mimeType: rendered.mimeType,
      alt: `${diagram.type} diagram`,
    });
  }
  return result;
}
