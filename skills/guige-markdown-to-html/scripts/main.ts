#!/usr/bin/env bun

import { existsSync } from "node:fs";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import yaml from "js-yaml";

import { processAssets, type AssetMode } from "./lib/assets";
import { processDiagrams, type DiagramFormat, type DiagramRenderOptions } from "./lib/diagrams";
import {
  buildManifest,
  renderMarkdown,
  type RenderOptions,
  type RenderProfile,
  type ThemeName,
  type CssMode,
  type LegendMode,
} from "./lib/renderer";

export interface CliOptions extends RenderOptions {
  inputPath: string;
  outputPath?: string;
  manifestPath?: string;
  manifestVersion?: 1 | 2;
  assetMode: AssetMode;
  assetDirectory?: string;
  cssOutputPath?: string;
  diagramFormat: DiagramFormat;
  diagramDirectory?: string;
  mermaidTheme?: DiagramRenderOptions["mermaidTheme"];
  mermaidScale?: number;
  mermaidWidth?: number;
  mermaidBackground?: string;
  dryRun: boolean;
  json: boolean;
}

export interface CliResult extends Record<string, unknown> {
  success: true;
  schemaVersion: 1 | 2;
  htmlPath: string;
  manifestPath: string | null;
  backupPath: string | null;
  dryRun: boolean;
}

const PROFILES = new Set<RenderProfile>(["web", "fragment", "wechat", "email", "bare"]);
const THEMES = new Set<ThemeName>(["default", "simple", "grace", "modern"]);
const ASSET_MODES = new Set<AssetMode>(["preserve", "copy", "embed", "download"]);
const CSS_MODES = new Set<CssMode>(["embedded", "inline", "external", "none"]);
const LEGEND_MODES = new Set<LegendMode>(["alt", "title", "alt-title", "title-alt", "none"]);

function takeValue(argv: string[], index: number, option: string): [string, number] {
  const argument = argv[index]!;
  if (argument.startsWith(`${option}=`)) return [argument.slice(option.length + 1), index];
  const value = argv[index + 1];
  if (!value || value.startsWith("--")) throw new Error(`${option} requires a value`);
  return [value, index + 1];
}

export function parseCliArgs(argv: string[]): CliOptions {
  let inputPath = "";
  const options: CliOptions = {
    inputPath: "",
    assetMode: "preserve",
    dryRun: false,
    json: false,
    diagramFormat: "source",
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index]!;
    if (!argument.startsWith("--")) {
      if (inputPath) throw new Error(`unexpected positional argument: ${argument}`);
      inputPath = argument;
      continue;
    }
    if (argument === "--dry-run") options.dryRun = true;
    else if (argument === "--json") options.json = true;
    else if (argument === "--cite") options.cite = true;
    else if (argument === "--no-cite") options.cite = false;
    else if (argument === "--keep-title") options.keepTitle = true;
    else if (argument === "--remove-title") options.keepTitle = false;
    else if (argument === "--allow-html") options.allowHtml = true;
    else if (argument === "--line-number") options.lineNumbers = true;
    else if (argument === "--count") options.count = true;
    else if (argument === "--mac-code-block") options.macCodeBlock = true;
    else if (argument === "--no-mac-code-block") options.macCodeBlock = false;
    else if (argument === "--no-diagrams") options.diagramFormat = "off";
    else if (argument === "--help" || argument === "-h") throw new Error("HELP");
    else {
      const flag = argument.split("=", 1)[0]!;
      const [value, consumed] = takeValue(argv, index, flag);
      index = consumed;
      if (flag === "--output") options.outputPath = value;
      else if (flag === "--manifest") options.manifestPath = value;
      else if (flag === "--profile") {
        if (!PROFILES.has(value as RenderProfile)) throw new Error(`invalid profile: ${value}`);
        options.profile = value as RenderProfile;
      } else if (flag === "--theme") {
        if (!THEMES.has(value as ThemeName)) throw new Error(`invalid theme: ${value}`);
        options.theme = value as ThemeName;
      } else if (flag === "--assets") {
        if (!ASSET_MODES.has(value as AssetMode)) throw new Error(`invalid asset mode: ${value}`);
        options.assetMode = value as AssetMode;
      } else if (flag === "--asset-dir") {
        if (!value.trim()) throw new Error("asset directory cannot be empty");
        options.assetDirectory = value;
      } else if (flag === "--css-mode") {
        if (!CSS_MODES.has(value as CssMode)) throw new Error(`invalid CSS mode: ${value}`);
        options.cssMode = value as CssMode;
      } else if (flag === "--css-output") {
        options.cssOutputPath = value;
      } else if (flag === "--legend") {
        if (!LEGEND_MODES.has(value as LegendMode)) throw new Error(`invalid legend mode: ${value}`);
        options.legend = value as LegendMode;
      } else if (flag === "--diagram-format") {
        if (!["source", "svg", "png", "off"].includes(value)) throw new Error(`invalid diagram format: ${value}`);
        options.diagramFormat = value as DiagramFormat;
      } else if (flag === "--diagram-dir") {
        options.diagramDirectory = value;
      } else if (flag === "--mermaid-theme") {
        if (!["default", "forest", "dark", "neutral", "base"].includes(value)) {
          throw new Error(`invalid Mermaid theme: ${value}`);
        }
        options.mermaidTheme = value as DiagramRenderOptions["mermaidTheme"];
      } else if (flag === "--mermaid-scale") {
        const scale = Number.parseFloat(value);
        if (!Number.isFinite(scale) || scale <= 0 || scale > 4) throw new Error("Mermaid scale must be greater than 0 and at most 4");
        options.mermaidScale = scale;
      } else if (flag === "--mermaid-width") {
        const width = Number.parseInt(value, 10);
        if (!Number.isInteger(width) || width <= 0) throw new Error("Mermaid width must be a positive integer");
        options.mermaidWidth = width;
      } else if (flag === "--mermaid-bg") {
        if (!["white", "transparent"].includes(value) && !/^#[0-9a-f]{3,8}$/i.test(value)) {
          throw new Error("Mermaid background must be white, transparent, or hexadecimal");
        }
        options.mermaidBackground = value;
      } else if (flag === "--manifest-version") {
        if (value !== "1" && value !== "2") throw new Error("manifest version must be 1 or 2");
        options.manifestVersion = Number(value) as 1 | 2;
      } else if (flag === "--color") options.color = value;
      else if (flag === "--title") options.title = value;
      else if (flag === "--font-family") options.fontFamily = value;
      else if (flag === "--font-size") options.fontSize = Number.parseInt(value.replace(/px$/i, ""), 10);
      else if (flag === "--code-theme") options.codeTheme = value;
      else if (flag === "--base-url") options.baseUrl = value;
      else throw new Error(`unknown option: ${flag}`);
    }
  }
  if (!inputPath) throw new Error("a Markdown input file is required");
  options.inputPath = inputPath;
  return options;
}

function configPaths(cwd = process.cwd()): string[] {
  const xdgRoot = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
  return [
    path.join(cwd, ".guige-skills", "guige-markdown-to-html", "EXTEND.md"),
    path.join(xdgRoot, "guige-skills", "guige-markdown-to-html", "EXTEND.md"),
    path.join(os.homedir(), ".guige-skills", "guige-markdown-to-html", "EXTEND.md"),
  ];
}

async function loadConfig(cwd = process.cwd()): Promise<Record<string, unknown>> {
  const configPath = configPaths(cwd).find(existsSync);
  if (!configPath) return {};
  const parsed = yaml.load(await readFile(configPath, "utf8"));
  return parsed && typeof parsed === "object" && !Array.isArray(parsed)
    ? parsed as Record<string, unknown>
    : {};
}

function configValue(config: Record<string, unknown>, name: string): unknown {
  return config[`default_${name}`] ?? config[name];
}

function withConfig(cli: CliOptions, config: Record<string, unknown>): CliOptions {
  const result = { ...cli };
  const stringOptions: Array<[keyof CliOptions, string]> = [
    ["profile", "profile"], ["theme", "theme"], ["color", "color"],
    ["fontFamily", "font_family"], ["codeTheme", "code_theme"], ["baseUrl", "base_url"],
    ["cssMode", "css_mode"],
  ];
  for (const [property, name] of stringOptions) {
    if (result[property] === undefined && typeof configValue(config, name) === "string") {
      (result as Record<string, unknown>)[property] = configValue(config, name);
    }
  }
  if (result.fontSize === undefined && configValue(config, "font_size") !== undefined) {
    result.fontSize = Number.parseInt(String(configValue(config, "font_size")).replace(/px$/i, ""), 10);
  }
  for (const [property, name] of [["cite", "cite"], ["keepTitle", "keep_title"]] as const) {
    if (result[property] === undefined && configValue(config, name) !== undefined) {
      const value = configValue(config, name);
      result[property] = typeof value === "boolean" ? value : /^(1|true|yes|on)$/i.test(String(value));
    }
  }
  if (!PROFILES.has((result.profile ?? "web") as RenderProfile)) throw new Error(`invalid profile in configuration: ${result.profile}`);
  if (!THEMES.has((result.theme ?? "default") as ThemeName)) throw new Error(`invalid theme in configuration: ${result.theme}`);
  return result;
}

function backupName(outputPath: string): string {
  const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 17);
  return `${outputPath}.bak-${timestamp}`;
}

export async function runCli(argv: string[], cwd = process.cwd()): Promise<CliResult> {
  const parsed = parseCliArgs(argv);
  const options = withConfig(parsed, await loadConfig(cwd));
  const sourcePath = path.resolve(cwd, options.inputPath);
  if (path.extname(sourcePath).toLowerCase() !== ".md" || !existsSync(sourcePath)) {
    throw new Error(`input must be an existing .md file: ${sourcePath}`);
  }
  const outputPath = path.resolve(cwd, options.outputPath ?? sourcePath.replace(/\.md$/i, ".html"));
  const manifestPath = options.manifestPath ? path.resolve(cwd, options.manifestPath) : null;
  const cssOutputPath = options.cssMode === "external"
    ? path.resolve(cwd, options.cssOutputPath ?? outputPath.replace(/\.html$/i, ".css"))
    : null;
  if (outputPath === sourcePath) throw new Error("output path must differ from the input Markdown path");
  if (manifestPath === sourcePath) throw new Error("manifest path must differ from the input Markdown path");
  if (manifestPath === outputPath) throw new Error("manifest path must differ from the HTML output path");
  if (cssOutputPath === sourcePath) throw new Error("stylesheet path must differ from the input Markdown path");
  if (cssOutputPath === outputPath) throw new Error("stylesheet path must differ from the HTML output path");
  if (cssOutputPath && cssOutputPath === manifestPath) throw new Error("stylesheet path must differ from the manifest path");
  if (cssOutputPath) {
    options.cssHref = path.relative(path.dirname(outputPath), cssOutputPath).split(path.sep).join("/");
  }
  const manifestVersion = options.manifestVersion ?? 2;
  const markdown = await readFile(sourcePath, "utf8");
  const withDiagrams = await processDiagrams(
    renderMarkdown(markdown, sourcePath, options),
    options.diagramFormat,
    outputPath,
    options.diagramDirectory,
    options.dryRun,
    undefined,
    {
      mermaidTheme: options.mermaidTheme ?? "default",
      mermaidScale: options.mermaidScale ?? 2,
      mermaidWidth: options.mermaidWidth ?? 860,
      mermaidBackground: options.mermaidBackground ?? "transparent",
    },
  );
  const rendered = await processAssets(
    withDiagrams,
    options.assetMode,
    sourcePath,
    outputPath,
    options.assetDirectory,
    options.dryRun,
  );
  const manifest = manifestVersion === 1
    ? buildManifest(rendered, sourcePath, outputPath, 1)
    : buildManifest(rendered, sourcePath, outputPath, 2);
  let backupPath: string | null = null;
  if (!options.dryRun) {
    await mkdir(path.dirname(outputPath), { recursive: true });
    if (existsSync(outputPath)) {
      backupPath = backupName(outputPath);
      await rename(outputPath, backupPath);
    }
    await writeFile(outputPath, rendered.html, "utf8");
    if (cssOutputPath) {
      await mkdir(path.dirname(cssOutputPath), { recursive: true });
      await writeFile(cssOutputPath, `${rendered.css}\n`, "utf8");
    }
    if (manifestPath) {
      await mkdir(path.dirname(manifestPath), { recursive: true });
      await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
    }
  }
  return {
    success: true,
    ...manifest,
    schemaVersion: manifestVersion,
    htmlPath: outputPath,
    manifestPath,
    backupPath,
    dryRun: options.dryRun,
  };
}

function usage(): string {
  return `Convert Markdown to general-purpose HTML

Usage:
  bun main.ts <markdown-file> [options]

Options:
  --output <path>              Output HTML path
  --profile <name>             web, fragment, wechat, email, bare (default: web)
  --theme <name>               default, simple, grace, modern
  --color <name|hex>           Primary accent color
  --font-family <name|css>     sans, serif, serif-cjk, mono, or CSS stack
  --font-size <14-18>          Base font size
  --code-theme <name>          Code color theme
  --title <text>               Override the document title
  --allow-html                 Preserve safe raw HTML after sanitization
  --line-number                Add line numbers to fenced code blocks
  --count                      Show word count and reading time
  --legend <mode>              alt, title, alt-title, title-alt, none
  --mac-code-block             Show a Mac-style code header
  --no-mac-code-block          Hide the Mac-style code header
  --diagram-format <mode>      source, svg, png, off
  --diagram-dir <path>         Static diagram output directory
  --no-diagrams                Remove Mermaid and PlantUML blocks
  --mermaid-theme <name>       default, forest, dark, neutral, base
  --mermaid-scale <0-4>        Mermaid render scale (default: 2)
  --mermaid-width <px>         Mermaid target width (default: 860)
  --mermaid-bg <value>         white, transparent, or hexadecimal
  --base-url <url>             Resolve root-relative links and canonical URLs
  --cite | --no-cite           Toggle bottom citations
  --keep-title | --remove-title
  --assets <mode>              preserve, copy, embed, download
  --asset-dir <path>           Asset folder relative to the HTML output
  --css-mode <mode>            embedded, inline, external, none
  --css-output <path>          Stylesheet path for external CSS mode
  --manifest <path>            Write a JSON manifest
  --manifest-version <1|2>     Generic v2 or legacy WeChat v1 (default: 2)
  --dry-run                    Validate and render without writing files
  --json                       Print a machine-readable result
  --help                       Show this help`;
}

if (import.meta.main) {
  try {
    const args = process.argv.slice(2);
    if (!args.length || args.includes("--help") || args.includes("-h")) {
      console.log(usage());
      process.exit(0);
    }
    const result = await runCli(args);
    console.log(args.includes("--json") ? JSON.stringify(result, null, 2) : result.htmlPath);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}
