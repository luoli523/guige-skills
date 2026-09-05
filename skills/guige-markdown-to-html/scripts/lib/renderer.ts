import { existsSync } from "node:fs";
import path from "node:path";
import { URL } from "node:url";

import { alert } from "@mdit/plugin-alert";
import { katex } from "@mdit/plugin-katex";
import hljs from "highlight.js";
import yaml from "js-yaml";
import juice from "juice";
import MarkdownIt, {
  type MarkdownIt as MarkdownItInstance,
  type RendererRule,
  type StateInline,
} from "markdown-it";
import footnote from "markdown-it-footnote";
import taskLists from "markdown-it-task-lists";
import sanitizeHtml from "sanitize-html";

export type RenderProfile = "web" | "fragment" | "wechat" | "email" | "bare";
export type ThemeName = "default" | "simple" | "grace" | "modern";
export type CssMode = "embedded" | "inline" | "external" | "none";
export type LegendMode = "alt" | "title" | "alt-title" | "title-alt" | "none";

export interface RenderOptions {
  profile?: RenderProfile;
  theme?: ThemeName;
  color?: string;
  fontFamily?: string;
  fontSize?: number;
  codeTheme?: string;
  cite?: boolean;
  keepTitle?: boolean;
  baseUrl?: string;
  cssMode?: CssMode;
  cssHref?: string;
  title?: string;
  allowHtml?: boolean;
  lineNumbers?: boolean;
  count?: boolean;
  legend?: LegendMode;
  macCodeBlock?: boolean;
}

export interface ContentAsset {
  type: "image";
  source: string;
  resolvedPath: string;
  alt: string;
  outputPath?: string;
  mimeType?: string;
  embedded?: boolean;
}

export interface DocumentMetadata {
  title: string;
  author: string;
  summary: string;
  language: string;
  canonicalUrl: string;
  cover: string;
  slug: string;
}

export interface RenderResult {
  html: string;
  contentHtml: string;
  profile: RenderProfile;
  theme: ThemeName;
  metadata: DocumentMetadata;
  assets: ContentAsset[];
  diagrams: DiagramAsset[];
  warnings: string[];
  sourceFrontmatter: Record<string, unknown>;
  options: Required<RenderOptions>;
  css: string;
  stats: DocumentStats;
}

export interface DocumentStats {
  words: number;
  characters: number;
  readingMinutes: number;
}

export interface DiagramAsset {
  type: "mermaid" | "plantuml";
  source: string;
  rendered: boolean;
  format?: "svg" | "png";
  outputPath?: string;
  mimeType?: string;
}

export type GenericManifest = {
  schemaVersion: 2;
  inputPath: string;
  htmlPath: string;
  outputMode: "document" | "fragment";
  profile: RenderProfile;
  theme: ThemeName;
  cssMode: CssMode;
  metadata: DocumentMetadata;
  assets: ContentAsset[];
  diagrams: DiagramAsset[];
  warnings: string[];
  stats: DocumentStats;
};

export type LegacyManifest = {
  schemaVersion: 1;
  htmlPath: string;
  assetBaseDir: string;
  title: string;
  summary: string;
  author: string;
  contentSourceUrl: string;
  cover: { source: string; resolvedPath: string } | null;
  contentImages: Array<{ source: string; resolvedPath: string; alt: string }>;
};

const DEFAULT_BASE_URL = "https://luoli523.github.io";
const COLOR_PRESETS: Record<string, string> = {
  blue: "#0F4C81",
  green: "#009874",
  vermilion: "#FA5151",
  yellow: "#FECE00",
  purple: "#92617E",
  sky: "#55C9EA",
  rose: "#B76E79",
  olive: "#556B2F",
  black: "#333333",
  gray: "#A9A9A9",
  pink: "#FFB7C5",
  red: "#A93226",
  orange: "#D97757",
};
const FONT_PRESETS: Record<string, string> = {
  sans: "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif",
  serif: "Optima,'PingFang SC',Georgia,'Times New Roman',serif",
  "serif-cjk": "'Source Han Serif SC','Noto Serif CJK SC',STSong,SimSun,serif",
  mono: "Menlo,Monaco,'Courier New',monospace",
};

function resolveOptions(options: RenderOptions): Required<RenderOptions> {
  const profile = options.profile ?? "web";
  const isWechat = profile === "wechat";
  const defaultCssMode: CssMode = profile === "wechat" || profile === "email"
    ? "inline"
    : profile === "web"
      ? "embedded"
      : "none";
  const fontSize = options.fontSize ?? 16;
  if (!Number.isInteger(fontSize) || fontSize < 14 || fontSize > 18) {
    throw new Error("font size must be an integer between 14 and 18");
  }
  const colorName = options.color ?? "blue";
  const fontName = options.fontFamily ?? "sans";
  const color = COLOR_PRESETS[colorName.toLowerCase()] ?? colorName;
  if (!/^#[0-9a-f]{3,8}$/i.test(color) && !/^[a-z]+$/i.test(color)) {
    throw new Error("color must be a preset name, CSS color name, or hexadecimal value");
  }
  const fontFamily = FONT_PRESETS[fontName.toLowerCase()] ?? fontName;
  if (!/^[\p{L}\p{N}\s,'"._-]+$/u.test(fontFamily)) {
    throw new Error("font family contains unsupported CSS characters");
  }
  return {
    profile,
    theme: options.theme ?? (isWechat ? "simple" : "default"),
    color,
    fontFamily,
    fontSize,
    codeTheme: options.codeTheme ?? "github",
    cite: options.cite ?? isWechat,
    keepTitle: options.keepTitle ?? !isWechat,
    baseUrl: (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, ""),
    cssMode: options.cssMode ?? defaultCssMode,
    cssHref: options.cssHref ?? "styles.css",
    title: options.title ?? "",
    allowHtml: options.allowHtml ?? false,
    lineNumbers: options.lineNumbers ?? false,
    count: options.count ?? false,
    legend: options.legend ?? "none",
    macCodeBlock: options.macCodeBlock ?? isWechat,
  };
}

function parseFrontmatter(markdown: string): {
  attributes: Record<string, unknown>;
  body: string;
} {
  const match = markdown.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);
  if (!match) return { attributes: {}, body: markdown };
  const parsed = yaml.load(match[1] ?? "");
  return {
    attributes: parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? parsed as Record<string, unknown>
      : {},
    body: markdown.slice(match[0].length),
  };
}

function textValue(value: unknown): string {
  if (value === null || value === undefined || value === false) return "";
  return typeof value === "string" || typeof value === "number" ? String(value).trim() : "";
}

function stripMarkdown(value: string): string {
  return value
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[`*_~>#-]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function deriveMetadata(
  frontmatter: Record<string, unknown>,
  body: string,
  sourcePath: string,
  baseUrl: string,
  titleOverride = "",
): DocumentMetadata {
  const heading = body.match(/^#{1,2}\s+(.+)$/m)?.[1] ?? "";
  const title = titleOverride || textValue(frontmatter.title) || stripMarkdown(heading) || path.basename(sourcePath, path.extname(sourcePath));
  const firstParagraph = body.split(/\n\s*\n/).find((part) => {
    const value = part.trim();
    return value && !value.startsWith("#") && !value.startsWith("```") && !value.startsWith("!");
  }) ?? "";
  const summary = textValue(frontmatter.description)
    || textValue(frontmatter.summary)
    || stripMarkdown(firstParagraph).slice(0, 120);
  const slug = textValue(frontmatter.slug) || path.basename(path.dirname(sourcePath));
  const explicitUrl = textValue(frontmatter.canonical_url)
    || textValue(frontmatter.canonicalUrl)
    || textValue(frontmatter.content_source_url)
    || textValue(frontmatter.source_url);
  const canonicalUrl = explicitUrl
    ? new URL(explicitUrl, `${baseUrl}/`).toString()
    : slug ? `${baseUrl}/p/${encodeURIComponent(slug)}/` : "";
  const cover = textValue(frontmatter.coverImage)
    || textValue(frontmatter.coverimage)
    || textValue(frontmatter.featureImage)
    || textValue(frontmatter.featureimage)
    || textValue(frontmatter.cover)
    || textValue(frontmatter.image);
  return {
    title,
    author: textValue(frontmatter.author),
    summary,
    language: textValue(frontmatter.lang) || textValue(frontmatter.language),
    canonicalUrl,
    cover,
    slug,
  };
}

function preprocessObsidianImages(markdown: string, sourcePath: string): string {
  const sourceDirectory = path.dirname(sourcePath);
  return markdown.replace(/!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]/g, (_match, rawSource: string, rawAlt?: string) => {
    const requested = rawSource.trim();
    const directPath = path.resolve(sourceDirectory, requested);
    const attachmentPath = path.resolve(sourceDirectory, "Attachments", requested);
    const resolvedSource = existsSync(directPath)
      ? requested
      : existsSync(attachmentPath)
        ? path.join("Attachments", requested)
        : requested;
    const portableSource = resolvedSource.split(path.sep).join("/");
    const alt = (rawAlt ?? "").replace(/\]/g, "\\]");
    return `![${alt}](<${portableSource}>)`;
  });
}

function createMarkdownIt(options: Required<RenderOptions>): MarkdownItInstance {
  const md: MarkdownItInstance = new MarkdownIt({
    html: options.allowHtml,
    linkify: true,
    typographer: false,
    highlight(code: string, language: string): string {
      const normalized = language.trim().toLowerCase();
      if (normalized && hljs.getLanguage(normalized)) {
        return hljs.highlight(code, { language: normalized, ignoreIllegals: true }).value;
      }
      return code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    },
  });
  // The plugins ship CommonJS-era MarkdownIt types that are structurally
  // incompatible with the current ESM declarations, although the runtime API
  // is the same. Invoke their standard plugin functions through a local shim.
  (footnote as unknown as (instance: MarkdownItInstance) => void)(md);
  (taskLists as unknown as (
    instance: MarkdownItInstance,
    pluginOptions: { enabled: boolean; label: boolean; labelAfter: boolean },
  ) => void)(md, { enabled: false, label: true, labelAfter: true });
  md.use(alert);
  md.use(katex, { throwOnError: false, strict: "ignore", output: "mathml" });

  md.inline.ruler.before("emphasis", "ruby", (state: StateInline, silent: boolean): boolean => {
    const match = state.src.slice(state.pos).match(/^\{([^{}|\n]+)\|([^{}\n]+)\}/);
    if (!match) return false;
    if (!silent) {
      const token = state.push("ruby", "ruby", 0);
      token.meta = { base: match[1]!, annotation: match[2]! };
    }
    state.pos += match[0].length;
    return true;
  });
  md.renderer.rules.ruby = (tokens, index) => {
    const meta = tokens[index]!.meta as { base: string; annotation: string };
    return `<ruby>${md.utils.escapeHtml(meta.base)}<rt>${md.utils.escapeHtml(meta.annotation)}</rt></ruby>`;
  };

  const defaultImage = md.renderer.rules.image;
  md.renderer.rules.image = (tokens, index, renderOptions, env, renderer) => {
    const imageHtml = defaultImage
      ? defaultImage(tokens, index, renderOptions, env, renderer)
      : renderer.renderToken(tokens, index, renderOptions);
    if (options.legend === "none") return imageHtml;
    const alt = tokens[index]!.content.trim();
    const title = String(tokens[index]!.attrGet("title") ?? "").trim();
    const parts = options.legend === "alt"
      ? [alt]
      : options.legend === "title"
        ? [title]
        : options.legend === "title-alt"
          ? [title, alt]
          : [alt, title];
    const caption = parts.filter(Boolean).map((item) => md.utils.escapeHtml(item)).join(" — ");
    return caption
      ? `<span class="image-figure">${imageHtml}<span class="image-caption">${caption}</span></span>`
      : imageHtml;
  };

  const defaultFence = md.renderer.rules.fence;
  md.renderer.rules.fence = (tokens, index, renderOptions, env, renderer) => {
    const language = tokens[index]!.info.trim().split(/\s+/, 1)[0]!.toLowerCase();
    if (language === "mermaid" || language === "plantuml") {
      const code = md.utils.escapeHtml(tokens[index]!.content);
      return `<pre class="diagram diagram-${language}" data-diagram-type="${language}"><code>${code}</code></pre>\n`;
    }
    return defaultFence
      ? defaultFence(tokens, index, renderOptions, env, renderer)
      : renderer.renderToken(tokens, index, renderOptions);
  };

  const renderToken: RendererRule = (tokens, index, renderOptions, _env, renderer) =>
    renderer.renderToken(tokens, index, renderOptions);
  const defaultLinkOpen: RendererRule = md.renderer.rules.link_open ?? renderToken;
  const defaultLinkClose: RendererRule = md.renderer.rules.link_close ?? renderToken;
  md.renderer.rules.link_open = (tokens, index, renderOptions, env, renderer) => {
    const hrefIndex = tokens[index]!.attrIndex("href");
    let href = String(hrefIndex >= 0 ? tokens[index]!.attrs![hrefIndex]![1] : "");
    if (href.startsWith("/") && options.baseUrl) {
      href = new URL(href, `${options.baseUrl}/`).toString();
      tokens[index]!.attrSet("href", href);
    }
    const isExternal = /^https?:\/\//i.test(href);
    const shouldCite = options.cite && isExternal && !href.startsWith("https://mp.weixin.qq.com/");
    const citationState = env as { citations?: Array<{ label: string; url: string }>; citationStack?: number[] };
    citationState.citations ??= [];
    citationState.citationStack ??= [];
    if (shouldCite) {
      let citationIndex = citationState.citations.findIndex((item) => item.url === href);
      if (citationIndex < 0) {
        citationState.citations.push({ label: "", url: href });
        citationIndex = citationState.citations.length - 1;
      }
      citationState.citationStack.push(citationIndex + 1);
    } else {
      citationState.citationStack.push(0);
    }
    return defaultLinkOpen(tokens, index, renderOptions, env, renderer);
  };
  md.renderer.rules.link_close = (tokens, index, renderOptions, env, renderer) => {
    const state = env as { citationStack?: number[] };
    const citation = state.citationStack?.pop() ?? 0;
    const suffix = citation ? `<sup>[${citation}]</sup>` : "";
    return suffix + defaultLinkClose(tokens, index, renderOptions, env, renderer);
  };
  return md;
}

function collectImages(tokens: ReturnType<MarkdownItInstance["parse"]>, sourcePath: string): ContentAsset[] {
  const assets: ContentAsset[] = [];
  const visit = (items: typeof tokens): void => {
    for (const token of items) {
      if (token.type === "image") {
        const source = String(token.attrGet("src") ?? "");
        const alt = token.content ?? "";
        assets.push({
          type: "image",
          source,
          resolvedPath: /^https?:\/\//i.test(source)
            ? source
            : path.resolve(path.dirname(sourcePath), source),
          alt,
        });
      }
      if (token.children) visit(token.children);
    }
  };
  visit(tokens);
  return assets;
}

function collectDiagrams(tokens: ReturnType<MarkdownItInstance["parse"]>): DiagramAsset[] {
  return tokens
    .filter((token) => token.type === "fence")
    .map((token) => ({ language: token.info.trim().split(/\s+/, 1)[0]!.toLowerCase(), source: token.content }))
    .filter((item): item is { language: "mermaid" | "plantuml"; source: string } =>
      item.language === "mermaid" || item.language === "plantuml")
    .map((item) => ({ type: item.language, source: item.source, rendered: false }));
}

function removeFirstDocumentHeading(tokens: ReturnType<MarkdownItInstance["parse"]>): void {
  const index = tokens.findIndex((token) => token.type === "heading_open" && ["h1", "h2"].includes(token.tag));
  if (index >= 0) tokens.splice(index, 3);
}

function sanitizeRenderedHtml(rendered: string): string {
  return sanitizeHtml(rendered, {
    allowedTags: [
      "a", "aside", "blockquote", "br", "code", "del", "div", "em", "h1", "h2", "h3", "h4", "h5", "h6",
      "annotation", "hr", "img", "input", "label", "li", "math", "maction", "maligngroup", "malignmark",
      "menclose", "merror", "mfenced", "mfrac", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover",
      "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msubsup",
      "msup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "ol", "p", "pre", "ruby", "rt",
      "s", "section", "semantics", "span", "strong",
      "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
    ],
    allowedAttributes: {
      "*": ["class", "id", "title", "aria-hidden"],
      a: ["href", "name", "aria-label"],
      img: ["src", "alt", "title"],
      input: ["type", "checked", "disabled"],
      ol: ["start"],
      pre: ["data-diagram-type"],
      annotation: ["encoding"],
      math: ["xmlns"],
      mtable: ["columnalign", "columnspacing", "rowspacing"],
      mtd: ["columnalign"],
      span: ["data-line"],
    },
    allowedSchemes: ["http", "https", "mailto"],
    allowedSchemesByTag: { img: ["http", "https", "data"] },
    allowProtocolRelative: false,
  });
}

function themeCss(options: Required<RenderOptions>): string {
  const accent = options.color;
  const modern = options.theme === "modern";
  const grace = options.theme === "grace";
  const darkCodeThemes = new Set(["dark", "github-dark", "monokai", "nord"]);
  const darkCode = darkCodeThemes.has(options.codeTheme.toLowerCase());
  const codeBackground = options.codeTheme.toLowerCase() === "nord"
    ? "#2e3440"
    : darkCode ? "#161b22" : "#f6f8fa";
  const codeForeground = darkCode ? "#e6edf3" : "#24292f";
  const codeComment = darkCode ? "#8b949e" : "#6a737d";
  const codeKeyword = darkCode ? "#ff7b72" : "#cf222e";
  const codeString = darkCode ? "#a5d6ff" : "#0a3069";
  const codeNumber = darkCode ? "#79c0ff" : "#0550ae";
  return [
    `.markdown-body{font-family:${options.fontFamily};font-size:${options.fontSize}px;line-height:${modern ? "2" : grace ? "1.9" : "1.75"};color:#30343b;max-width:860px;margin:0 auto;padding:${modern ? "24px" : "16px"};overflow-wrap:anywhere}`,
    `.markdown-body h1{font-size:2em;margin:1.4em 0 .8em;color:${accent}}`,
    `.markdown-body h2{font-size:1.55em;margin:1.6em 0 .7em;padding-bottom:.3em;border-bottom:2px solid ${accent}}`,
    `.markdown-body h3{font-size:1.25em;margin:1.5em 0 .6em;padding-left:.65em;border-left:4px solid ${accent}}`,
    `.markdown-body p{margin:1em 0}`,
    `.markdown-body a{color:${accent};text-decoration:none}`,
    `.markdown-body blockquote{margin:1.2em 0;padding:.8em 1em;border-left:4px solid ${accent};background:#f6f8fa}`,
    `.markdown-body table{border-collapse:collapse;width:100%;margin:1.2em 0}`,
    `.markdown-body th,.markdown-body td{border:1px solid #d8dee4;padding:.45em .65em;text-align:left}`,
    `.markdown-body th{background:${accent};color:#fff}`,
    `.markdown-body img{display:block;max-width:100%;height:auto;margin:1.2em auto}`,
    `.markdown-body pre{overflow:auto;padding:1em;border-radius:8px;color:${codeForeground};background:${codeBackground}}`,
    `.markdown-body code{font-family:${FONT_PRESETS.mono};font-size:.9em}`,
    `.markdown-body :not(pre)>code{padding:.15em .35em;border-radius:4px;background:#f1f3f5;color:#d14}`,
    `.markdown-body .task-list-item{list-style:none}`,
    `.markdown-body .footnotes{margin-top:2em;font-size:.9em;color:#57606a}`,
    `.markdown-body .markdown-alert{padding:.7em 1em;margin:1em 0;border-left:4px solid ${accent};background:#f6f8fa}`,
    `.markdown-body .markdown-alert-title{font-weight:700;color:${accent}}`,
    `.markdown-body ruby rt{font-size:.65em;color:#57606a}`,
    `.markdown-body .diagram{white-space:pre-wrap;border:1px dashed #8c959f}`,
    `.markdown-body .katex{font-size:1.05em}`,
    `.markdown-body .code-line{display:block;counter-increment:code-line}`,
    `.markdown-body .code-line:before{content:attr(data-line);display:inline-block;width:2.5em;margin-right:1em;color:#8c959f;text-align:right;user-select:none}`,
    `.markdown-body .document-stats{margin:.5em 0 1.5em;color:#6e7781;font-size:.85em}`,
    `.markdown-body .image-figure{display:block;margin:1.2em auto;text-align:center}`,
    `.markdown-body .image-figure img{margin:.2em auto}`,
    `.markdown-body .image-caption{display:block;margin-top:.45em;color:#6e7781;font-size:.85em}`,
    `.markdown-body .mac-code-header{display:block;padding:.55em .8em 0;color:#ed6a5e;letter-spacing:.25em}`,
    `.markdown-body .hljs-comment,.markdown-body .hljs-quote{color:${codeComment}}`,
    `.markdown-body .hljs-keyword,.markdown-body .hljs-selector-tag,.markdown-body .hljs-built_in{color:${codeKeyword}}`,
    `.markdown-body .hljs-string,.markdown-body .hljs-title,.markdown-body .hljs-section{color:${codeString}}`,
    `.markdown-body .hljs-number,.markdown-body .hljs-literal,.markdown-body .hljs-variable{color:${codeNumber}}`,
  ].join("\n");
}

function addCodeLineNumbers(content: string): string {
  return content.replace(/(<pre><code[^>]*>)([\s\S]*?)(<\/code><\/pre>)/g, (_match, open: string, code: string, close: string) => {
    const normalized = code.endsWith("\n") ? code.slice(0, -1) : code;
    const lines = normalized.split("\n").map((line, index) =>
      `<span class="code-line" data-line="${index + 1}">${line || " "}</span>`).join("\n");
    return `${open}${lines}${close}`;
  });
}

function addMacCodeHeaders(content: string): string {
  return content.replace(
    /<pre><code/g,
    '<pre><span class="mac-code-header" aria-hidden="true">● ● ●</span><code',
  );
}

function documentStats(markdown: string): DocumentStats {
  const plain = stripMarkdown(markdown);
  const cjkCharacters = plain.match(/[\u3400-\u9fff\uf900-\ufaff]/g)?.length ?? 0;
  const nonCjkWords = plain.replace(/[\u3400-\u9fff\uf900-\ufaff]/g, " ").match(/[\p{L}\p{N}]+/gu)?.length ?? 0;
  const words = cjkCharacters + nonCjkWords;
  return {
    words,
    characters: plain.length,
    readingMinutes: Math.max(1, Math.ceil(words / 300)),
  };
}

function documentHtml(title: string, content: string, css = "", language = "", cssHref = ""): string {
  const lang = language ? ` lang="${sanitizeHtml(language, { allowedTags: [], allowedAttributes: {} })}"` : "";
  const style = css ? `<style>\n${css}\n</style>` : "";
  const stylesheet = cssHref ? `<link rel="stylesheet" href="${sanitizeHtml(cssHref, { allowedTags: [], allowedAttributes: {} })}">` : "";
  return `<!doctype html><html${lang}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${sanitizeHtml(title, { allowedTags: [], allowedAttributes: {} })}</title>${style}${stylesheet}</head><body>${content}</body></html>`;
}

export function renderMarkdown(
  markdown: string,
  sourcePath: string,
  inputOptions: RenderOptions = {},
): RenderResult {
  const options = resolveOptions(inputOptions);
  const { attributes, body } = parseFrontmatter(markdown);
  const preparedBody = preprocessObsidianImages(body, sourcePath);
  const metadata = deriveMetadata(attributes, preparedBody, sourcePath, options.baseUrl, options.title);
  const stats = documentStats(preparedBody);
  const md = createMarkdownIt(options);
  const env: { citations: Array<{ label: string; url: string }>; citationStack: number[] } = {
    citations: [],
    citationStack: [],
  };
  const tokens = md.parse(preparedBody, env);
  const assets = collectImages(tokens, sourcePath);
  const diagrams = collectDiagrams(tokens);
  if (!options.keepTitle) removeFirstDocumentHeading(tokens);
  let content = md.renderer.render(tokens, md.options, env);
  if (options.profile === "wechat") {
    const rawHighlight = attributes.highlight ?? attributes.wechat_highlight;
    const highlightDisabled = rawHighlight === false
      || ["0", "false", "no", "off", "none"].includes(textValue(rawHighlight).toLowerCase());
    const highlight = highlightDisabled ? "" : textValue(rawHighlight) || metadata.summary;
    if (highlight) {
      content = `<blockquote class="lead-callout">${md.renderInline(highlight, env)}</blockquote>${content}`;
    }
  }
  content = content.replace(/<code class="language-([^"]+)"/g, '<code class="hljs language-$1"');
  if (options.lineNumbers) content = addCodeLineNumbers(content);
  if (options.macCodeBlock) content = addMacCodeHeaders(content);
  if (env.citations.length) {
    const items = env.citations.map((item, index) => `<li><a href="${md.utils.escapeHtml(item.url)}">[${index + 1}] ${md.utils.escapeHtml(item.url)}</a></li>`).join("");
    content += `<section class="references"><h2>参考链接</h2><ol>${items}</ol></section>`;
  }
  if (options.count) {
    content = `<aside class="document-stats">${stats.words} words · ${stats.readingMinutes} min read</aside>${content}`;
  }
  content = sanitizeRenderedHtml(content);
  const css = themeCss(options);
  let contentHtml = `<article class="markdown-body">${content}</article>`;
  if (options.cssMode === "inline") {
    const inlinedDocument = juice(documentHtml(metadata.title, contentHtml, css, metadata.language), {
      removeStyleTags: true,
      preserveMediaQueries: false,
    });
    contentHtml = inlinedDocument.match(/<body[^>]*>([\s\S]*)<\/body>/i)?.[1] ?? contentHtml;
  }
  const html = options.profile === "fragment" || options.profile === "bare"
    ? contentHtml
    : documentHtml(
      metadata.title,
      contentHtml,
      options.cssMode === "embedded" ? css : "",
      metadata.language,
      options.cssMode === "external" ? options.cssHref : "",
    );
  return {
    html,
    contentHtml,
    profile: options.profile,
    theme: options.theme,
    metadata,
    assets,
    diagrams,
    warnings: diagrams.map((diagram) =>
      `${diagram.type} diagram kept as source; static rendering is unavailable in this render mode`),
    sourceFrontmatter: attributes,
    options,
    css,
    stats,
  };
}

function resolveAsset(source: string, sourcePath: string): string {
  return /^https?:\/\//i.test(source) ? source : path.resolve(path.dirname(sourcePath), source);
}

export function buildManifest(
  result: RenderResult,
  sourcePath: string,
  htmlPath: string,
  version: 2,
): GenericManifest;
export function buildManifest(
  result: RenderResult,
  sourcePath: string,
  htmlPath: string,
  version: 1,
): LegacyManifest;
export function buildManifest(
  result: RenderResult,
  sourcePath: string,
  htmlPath: string,
  version?: undefined,
): GenericManifest;
export function buildManifest(
  result: RenderResult,
  sourcePath: string,
  htmlPath: string,
  version: 1 | 2 = 2,
): GenericManifest | LegacyManifest {
  if (version === 2) {
    return {
      schemaVersion: 2,
      inputPath: path.resolve(sourcePath),
      htmlPath: path.resolve(htmlPath),
      outputMode: result.profile === "fragment" || result.profile === "bare" ? "fragment" : "document",
      profile: result.profile,
      theme: result.theme,
      cssMode: result.options.cssMode,
      metadata: result.metadata,
      assets: result.assets,
      diagrams: result.diagrams,
      warnings: result.warnings,
      stats: result.stats,
    };
  }
  const fallbackCover = result.metadata.cover || result.assets[0]?.source || "";
  return {
    schemaVersion: 1,
    htmlPath: path.resolve(htmlPath),
    assetBaseDir: path.dirname(path.resolve(sourcePath)),
    title: result.metadata.title,
    summary: result.metadata.summary,
    author: result.metadata.author || "鬼哥",
    contentSourceUrl: result.metadata.canonicalUrl,
    cover: fallbackCover
      ? { source: fallbackCover, resolvedPath: resolveAsset(fallbackCover, sourcePath) }
      : null,
    contentImages: result.assets.map(({ source, resolvedPath, alt }) => ({ source, resolvedPath, alt })),
  };
}
