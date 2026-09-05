import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

import type { ContentAsset, RenderResult } from "./renderer";

export type AssetMode = "preserve" | "copy" | "embed" | "download";

const MIME_BY_EXTENSION: Record<string, string> = {
  ".avif": "image/avif",
  ".gif": "image/gif",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
};
const MAX_REMOTE_IMAGE_BYTES = 20 * 1024 * 1024;
const EXTENSION_BY_MIME: Record<string, string> = {
  "image/avif": ".avif",
  "image/gif": ".gif",
  "image/jpeg": ".jpg",
  "image/png": ".png",
  "image/webp": ".webp",
};

function htmlAttribute(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function safeFilename(source: string, index: number): string {
  let candidate = "";
  try {
    candidate = new URL(source).pathname;
  } catch {
    candidate = source;
  }
  const basename = path.basename(candidate).replace(/[^A-Za-z0-9._-]/g, "-");
  return basename && basename !== "." ? basename : `image-${index + 1}`;
}

function mimeType(source: string, header = ""): string {
  const normalizedHeader = header.split(";", 1)[0]!.trim().toLowerCase();
  if (normalizedHeader.startsWith("image/") && normalizedHeader !== "image/svg+xml") return normalizedHeader;
  return MIME_BY_EXTENSION[path.extname(new URL(source, "file:///tmp/").pathname).toLowerCase()] ?? "application/octet-stream";
}

function isPrivateNetworkUrl(source: string): boolean {
  const url = new URL(source);
  const host = url.hostname.toLowerCase().replace(/^\[|\]$/g, "");
  return host === "localhost"
    || host.endsWith(".local")
    || host === "::1"
    || host.startsWith("127.")
    || host.startsWith("10.")
    || host.startsWith("192.168.")
    || /^172\.(1[6-9]|2\d|3[01])\./.test(host)
    || host === "169.254.169.254";
}

async function downloadImage(source: string): Promise<{ bytes: Uint8Array; mime: string }> {
  const url = new URL(source);
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error(`unsupported remote image protocol: ${url.protocol}`);
  if (isPrivateNetworkUrl(source)) throw new Error(`refusing to download an image from a private network: ${source}`);
  const response = await fetch(url, { redirect: "follow" });
  if (response.url && isPrivateNetworkUrl(response.url)) {
    throw new Error(`refusing to download an image redirected to a private network: ${response.url}`);
  }
  if (!response.ok) throw new Error(`image download failed with HTTP ${response.status}: ${source}`);
  const declaredLength = Number(response.headers.get("content-length") ?? "0");
  if (declaredLength > MAX_REMOTE_IMAGE_BYTES) throw new Error(`remote image exceeds 20 MiB: ${source}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  if (bytes.byteLength > MAX_REMOTE_IMAGE_BYTES) throw new Error(`remote image exceeds 20 MiB: ${source}`);
  const mime = mimeType(source, response.headers.get("content-type") ?? "");
  if (!mime.startsWith("image/") || mime === "image/svg+xml") {
    throw new Error(`remote resource is not a supported raster image: ${source}`);
  }
  return { bytes, mime };
}

function rewriteImageSource(result: RenderResult, source: string, replacement: string): void {
  const current = `src="${htmlAttribute(source)}"`;
  const next = `src="${htmlAttribute(replacement)}"`;
  result.html = result.html.split(current).join(next);
  result.contentHtml = result.contentHtml.split(current).join(next);
}

export async function processAssets(
  result: RenderResult,
  mode: AssetMode,
  sourcePath: string,
  htmlPath: string,
  assetDirectory = "assets",
  dryRun = false,
): Promise<RenderResult> {
  if (mode === "preserve") return result;
  const outputDirectory = path.resolve(path.dirname(htmlPath), assetDirectory);
  const usedNames = new Set<string>();
  for (let index = 0; index < result.assets.length; index += 1) {
    const asset = result.assets[index]!;
    const remote = /^https?:\/\//i.test(asset.source);
    if (mode === "copy" && remote) {
      result.warnings.push(`remote image preserved in copy mode: ${asset.source}`);
      continue;
    }
    if (remote && dryRun) {
      result.warnings.push(`remote image not fetched during dry-run: ${asset.source}`);
      continue;
    }
    let bytes: Uint8Array;
    let mime: string;
    if (remote) {
      ({ bytes, mime } = await downloadImage(asset.source));
    } else {
      bytes = new Uint8Array(await readFile(asset.resolvedPath));
      mime = mimeType(asset.resolvedPath);
    }
    if (mode === "embed") {
      const dataUrl = `data:${mime};base64,${Buffer.from(bytes).toString("base64")}`;
      rewriteImageSource(result, asset.source, dataUrl);
      asset.mimeType = mime;
      asset.embedded = true;
      continue;
    }
    let filename = safeFilename(asset.source, index);
    if (!path.extname(filename) && EXTENSION_BY_MIME[mime]) filename += EXTENSION_BY_MIME[mime];
    if (usedNames.has(filename)) filename = `${index + 1}-${filename}`;
    usedNames.add(filename);
    const outputPath = path.join(outputDirectory, filename);
    const relativePath = path.relative(path.dirname(htmlPath), outputPath).split(path.sep).join("/");
    if (!dryRun) {
      await mkdir(outputDirectory, { recursive: true });
      if (remote) await writeFile(outputPath, bytes);
      else if (path.resolve(asset.resolvedPath) !== path.resolve(outputPath)) {
        await copyFile(asset.resolvedPath, outputPath);
      }
    }
    rewriteImageSource(result, asset.source, relativePath);
    asset.outputPath = outputPath;
    asset.mimeType = mime;
  }
  return result;
}
