#!/usr/bin/env python3
"""Render Markdown to standalone, WeChat-friendly HTML using only Python's standard library."""

import argparse
import dataclasses
import html
import json
import os
import pathlib
import re
import sys
from typing import Dict, List, Optional, Tuple


THEMES = {"default", "simple", "grace", "modern"}
COLORS = {
    "blue": "#0F4C81", "green": "#009874", "vermilion": "#FA5151",
    "yellow": "#FECE00", "purple": "#92617E", "sky": "#55C9EA",
    "rose": "#B76E79", "olive": "#556B2F", "black": "#333333",
    "gray": "#A9A9A9", "pink": "#FFB7C5", "red": "#A93226", "orange": "#D97757",
}
FONTS = {
    "sans": "-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',Arial,sans-serif",
    "serif": "Optima,'PingFang SC',Georgia,'Times New Roman',serif",
    "serif-cjk": "'Source Han Serif SC','Noto Serif CJK SC',STSong,SimSun,serif",
    "mono": "Menlo,Monaco,'Courier New',monospace",
}

LANGUAGE_ALIASES = {
    "": "text", "txt": "text", "plain": "text", "plaintext": "text",
    "console": "bash", "terminal": "bash", "shell": "bash", "sh": "bash", "zsh": "bash",
    "yml": "yaml", "md": "markdown", "mkd": "markdown", "js": "javascript",
    "ts": "typescript", "py": "python",
}
CODE_COLORS = {
    "attr": "#79c0ff", "built_in": "#d2a8ff", "bullet": "#f2cc60", "comment": "#8b949e",
    "keyword": "#ff7b72", "literal": "#79c0ff", "meta": "#79c0ff", "number": "#79c0ff",
    "section": "#79c0ff", "string": "#a5d6ff", "variable": "#ffa657",
}
BASH_BUILTINS = {"awk", "brew", "bun", "cat", "cd", "chmod", "claude", "codex", "cp", "curl", "echo", "export", "find", "git", "grep", "jq", "ln", "ls", "mkdir", "mv", "npm", "npx", "pip", "pnpm", "python", "python3", "rg", "rm", "rsync", "sed", "ssh", "tar", "uv", "vim", "yarn"}
BASH_KEYWORDS = {"case", "do", "done", "elif", "else", "esac", "fi", "for", "function", "if", "in", "then", "until", "while"}


@dataclasses.dataclass
class RenderOptions:
    theme: str = "modern"
    color: str = "#0F4C81"
    font_family: str = FONTS["sans"]
    font_size: str = "16px"
    code_theme: str = "monokai"
    mac_code_block: bool = True
    cite: bool = True
    keep_title: bool = False


@dataclasses.dataclass
class RenderResult:
    title: str
    summary: str
    author: str
    frontmatter: Dict[str, str]
    content_html: str
    html: str
    content_images: List[Dict[str, str]]
    options: RenderOptions


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_config(text: str) -> Dict[str, str]:
    config: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip().lower()] = strip_quotes(value)
    return config


def config_paths() -> List[pathlib.Path]:
    project = pathlib.Path.cwd() / ".guige-skills" / "guige-markdown-to-html" / "EXTEND.md"
    xdg_root = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config"))
    return [
        project,
        xdg_root / "guige-skills" / "guige-markdown-to-html" / "EXTEND.md",
        pathlib.Path.home() / ".guige-skills" / "guige-markdown-to-html" / "EXTEND.md",
    ]


def load_config() -> Dict[str, str]:
    for path in config_paths():
        if path.is_file():
            return parse_config(path.read_text("utf-8"))
    return {}


def normalize_color(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return COLORS["blue"]
    return COLORS.get(candidate.lower(), candidate)


def normalize_font(value: str) -> str:
    return FONTS.get(value.strip().lower(), value.strip() or FONTS["sans"])


def normalize_font_size(value: str) -> str:
    candidate = value.strip()
    if candidate.isdigit():
        candidate += "px"
    if not re.fullmatch(r"1[4-8]px", candidate):
        raise ValueError("font size must be between 14px and 18px")
    return candidate


def normalize_code_language(language: str = "") -> str:
    language = re.sub(r"^\\{?\\.?", "", (language or "").strip().lower()).rstrip("}")
    return LANGUAGE_ALIASES.get(language, language or "text")


def code_escape(text: str) -> str:
    return html.escape(text.replace("\t", "    "), quote=False).replace(" ", "&nbsp;")


def code_span(kind: str, text: str) -> str:
    return f'<span class="hljs-{kind.replace("_", "-")}" style="color:{CODE_COLORS.get(kind, CODE_COLORS["literal"])};">{code_escape(text)}</span>'


def split_comment(line: str) -> Tuple[str, str]:
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote:
            if char == quote:
                quote = ""
        elif char in {"'", '"'}:
            quote = char
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index], line[index:]
    return line, ""


def highlight_scalar(value: str) -> str:
    token_re = re.compile(r'''("(?:\\.|[^"])*"|'(?:\\.|[^'])*'|\b(?:true|false|null|yes|no|on|off)\b|-?\b\d+(?:\.\d+)?\b)''', re.I)
    prefix, comment = split_comment(value)
    output: List[str] = []
    position = 0
    for match in token_re.finditer(prefix):
        output.append(code_escape(prefix[position:match.start()]))
        token = match.group(0)
        kind = "string" if token.startswith(("'", '"')) else "number" if re.match(r"-?\d", token) else "literal"
        output.append(code_span(kind, token))
        position = match.end()
    output.append(code_escape(prefix[position:]))
    if comment:
        output.append(code_span("comment", comment))
    return "".join(output)


def highlight_bash(line: str) -> str:
    prefix, comment = split_comment(line)
    token_re = re.compile(r'''('(?:\\.|[^'])*'|"(?:\\.|[^"])*"|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|\$[0-9@#?*-]|--?[A-Za-z0-9][A-Za-z0-9_-]*|\b[A-Za-z_][A-Za-z0-9_.-]*\b)''')
    output: List[str] = []
    position = 0
    for match in token_re.finditer(prefix):
        output.append(code_escape(prefix[position:match.start()]))
        token = match.group(0)
        kind = "string" if token.startswith(("'", '"')) else "variable" if token.startswith("$") else "attr" if token.startswith("-") else "keyword" if token in BASH_KEYWORDS else "built_in" if token in BASH_BUILTINS else ""
        output.append(code_span(kind, token) if kind else code_escape(token))
        position = match.end()
    output.append(code_escape(prefix[position:]))
    if comment:
        output.append(code_span("comment", comment))
    return "".join(output)


def highlight_yaml(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return ""
    if stripped.startswith("#"):
        return code_span("comment", line)
    if stripped in {"---", "..."}:
        return code_span("meta", line)
    match = re.match(r"^(\s*)([^:#][^:]*?)(\s*:\s*)(.*)$", line)
    if match:
        return code_escape(match.group(1)) + code_span("attr", match.group(2)) + code_escape(match.group(3)) + highlight_scalar(match.group(4))
    return highlight_scalar(line)


def highlight_json(line: str) -> str:
    token_re = re.compile(r'"(?:\\.|[^"\\])*"|-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b|\b(?:true|false|null)\b')
    output: List[str] = []
    position = 0
    for match in token_re.finditer(line):
        output.append(code_escape(line[position:match.start()]))
        token = match.group(0)
        kind = "attr" if token.startswith('"') and line[match.end():].lstrip().startswith(":") else "string" if token.startswith('"') else "number" if re.match(r"-?\d", token) else "literal"
        output.append(code_span(kind, token))
        position = match.end()
    return "".join(output) + code_escape(line[position:])


def highlight_toml(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("#"):
        return code_span("comment", line)
    if stripped.startswith("[") and stripped.endswith("]"):
        return code_span("section", line)
    match = re.match(r"^(\s*)([A-Za-z0-9_.-]+)(\s*=\s*)(.*)$", line)
    if match:
        return code_escape(match.group(1)) + code_span("attr", match.group(2)) + code_escape(match.group(3)) + highlight_scalar(match.group(4))
    return highlight_scalar(line)


def highlight_markdown(line: str) -> str:
    stripped = line.lstrip()
    indent = line[:len(line) - len(stripped)]
    if stripped.startswith("#"):
        match = re.match(r"^(#+\s*)", stripped)
        if match:
            return code_escape(indent) + code_span("section", match.group(1)) + code_escape(stripped[match.end():])
    if stripped in {"---", "..."} or stripped.startswith("```"):
        return code_escape(indent) + code_span("meta", stripped)
    if re.match(r"^[-*+]\s+", stripped):
        return code_escape(indent) + code_span("bullet", stripped[:2]) + code_escape(stripped[2:])
    return code_escape(line)


def highlight_code(code: str, language: str) -> str:
    highlighter = {"bash": highlight_bash, "yaml": highlight_yaml, "json": highlight_json, "toml": highlight_toml, "markdown": highlight_markdown}.get(normalize_code_language(language), code_escape)
    return "<br>".join(highlighter(line) for line in code.split("\n"))


def resolve_options(config: Dict[str, str], **overrides: Optional[object]) -> RenderOptions:
    def pick(name: str, default: object) -> object:
        explicit = overrides.get(name)
        return explicit if explicit is not None else config.get("default_" + name, config.get(name, default))

    theme = str(pick("theme", "modern")).lower()
    if theme not in THEMES:
        raise ValueError("theme must be one of: " + ", ".join(sorted(THEMES)))
    return RenderOptions(
        theme=theme,
        color=normalize_color(str(pick("color", COLORS["blue"]))),
        font_family=normalize_font(str(pick("font_family", "sans"))),
        font_size=normalize_font_size(str(pick("font_size", "16"))),
        code_theme=str(pick("code_theme", "monokai")),
        mac_code_block=bool(pick("mac_code_block", True)) if isinstance(pick("mac_code_block", True), bool)
        else parse_bool(str(pick("mac_code_block", True))),
        cite=bool(pick("cite", True)) if isinstance(pick("cite", True), bool)
        else parse_bool(str(pick("cite", True))),
        keep_title=bool(pick("keep_title", False)) if isinstance(pick("keep_title", False), bool)
        else parse_bool(str(pick("keep_title", False))),
    )


def parse_frontmatter(markdown: str) -> Tuple[Dict[str, str], str]:
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$", markdown)
    if not match:
        return {}, markdown
    return parse_config(match.group(1)), match.group(2)


def extract_title(body: str, fallback: str) -> str:
    heading = re.search(r"^#{1,2}\s+(.+?)\s*$", body, flags=re.MULTILINE)
    return heading.group(1).strip() if heading else fallback


def extract_summary(body: str) -> str:
    for paragraph in re.split(r"\n\s*\n", body):
        candidate = re.sub(r"^#+\s+", "", paragraph).strip()
        if candidate and not candidate.startswith(("```", "!", "|", ">")):
            return re.sub(r"\s+", " ", candidate)[:120]
    return ""


def style_map(options: RenderOptions) -> Dict[str, str]:
    color = options.color
    styles = {
        "article": f"font-family:{options.font_family};font-size:{options.font_size};line-height:1.85;color:#3f3f3f;",
        "h1": f"font-size:24px;line-height:1.35;font-weight:700;color:#111827;border-bottom:3px solid {color};padding-bottom:.35em;margin:1.2em 0 .8em;",
        "h2": f"display:table;margin:3em auto 1.5em;color:#fff;background:{color};font-size:19px;font-weight:700;text-align:center;padding:.25em .75em;",
        "h3": f"font-size:18px;font-weight:700;color:#3f3f3f;margin:2em 8px .75em 0;padding-left:8px;border-left:3px solid {color};",
        "p": "margin:1.2em 8px;color:#3f3f3f;",
        "blockquote": f"border-left:4px solid {color};border-radius:6px;background:#f7f7f7;color:#57534e;padding:1em;margin:1.2em 0;",
        "ul": "padding-left:1.5em;margin:1em 0;",
        "ol": "padding-left:1.7em;margin:1em 0;",
        "li": "margin:.5em 0;",
        "table": "width:100%;border-collapse:collapse;margin:1.2em 0;font-size:14px;",
        "th": f"border:1px solid #e5e7eb;background:{color};color:#fff;padding:.55em;text-align:left;",
        "td": "border:1px solid #e5e7eb;padding:.55em;",
        "code": "font-family:Menlo,Monaco,Consolas,monospace;font-size:90%;color:#c7254e;background:#f9f2f4;padding:2px 4px;border-radius:3px;",
        "pre": "margin:1em 0;border-radius:8px;overflow-x:auto;background:#f6f8fa;padding:1em;color:#24292e;line-height:1.55;",
        "img": "display:block;max-width:100%;height:auto;margin:1.2em auto;border-radius:6px;",
        "hr": "border:0;border-top:1px solid #e5e7eb;margin:2em 0;",
    }
    if options.theme == "simple":
        styles["h1"] = f"font-size:24px;font-weight:700;color:{color};margin:1.2em 0 .8em;"
        styles["h2"] = "font-size:20px;font-weight:700;color:#111827;margin:1.8em 0 .8em;"
    elif options.theme == "grace":
        styles["article"] = f"font-family:{options.font_family};font-size:{options.font_size};line-height:1.9;color:#374151;"
        styles["blockquote"] = f"border-top:2px solid {color};border-radius:8px;background:#fff7ed;color:#57534e;padding:1em;margin:1.2em 0;"
    elif options.theme == "modern":
        styles["article"] = f"font-family:{options.font_family};font-size:{options.font_size};line-height:2;color:#3f3f3f;padding:12px;border-radius:16px;background:#faf9f5;"
        styles["h1"] = f"display:table;margin:20px auto;padding:.3em 1em;border-radius:15px;color:#fff;background:{color};font-size:28px;font-weight:700;text-align:center;"
        styles["h2"] = f"display:block;margin:0 0 20px;padding:.2em 0;border-bottom:2px solid {color};background:transparent;color:{color};text-align:left;"
    if options.code_theme.lower() in {"dark", "github-dark", "monokai", "nord"}:
        styles["pre"] = "margin:1em 0;border-radius:8px;overflow-x:auto;background:#161b22;padding:1em;color:#e6edf3;line-height:1.55;"
    return styles


def inline(text: str, citations: List[Tuple[str, str]], cite: bool) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", lambda m: f'<code style="{CODE_STYLE}">{m.group(1)}</code>', escaped)
    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: m.group(0), escaped)

    def link(match: re.Match) -> str:
        label, url = match.group(1), html.unescape(match.group(2))
        if cite and re.match(r"https?://", url) and not url.startswith("https://mp.weixin.qq.com"):
            try:
                index = next(i for i, item in enumerate(citations, 1) if item[1] == url)
            except StopIteration:
                citations.append((label, url))
                index = len(citations)
            return f'<a href="{html.escape(url, quote=True)}">{label}<sup>[{index}]</sup></a>'
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


CODE_STYLE = "font-family:Menlo,Monaco,Consolas,monospace;font-size:90%;color:#c7254e;background:#f9f2f4;padding:2px 4px;border-radius:3px;"


def render_markdown(markdown: str, source_path: pathlib.Path, options: RenderOptions) -> RenderResult:
    frontmatter, body = parse_frontmatter(markdown)
    title = frontmatter.get("title", "") or extract_title(body, source_path.stem)
    summary = frontmatter.get("description", frontmatter.get("summary", "")) or extract_summary(body)
    author = frontmatter.get("author", "")
    styles = style_map(options)
    citations: List[Tuple[str, str]] = []
    images: List[Dict[str, str]] = []
    output: List[str] = []
    lines = body.splitlines()
    i = 0
    first_heading_removed = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            language = stripped[3:].strip() or "text"
            i += 1
            code_lines: List[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            normalized_language = normalize_code_language(language)
            header = "<div style=\"color:#8c959f;font-size:12px;margin-bottom:8px;\">● ● ●" + (f" &nbsp;{html.escape(normalized_language)}" if options.mac_code_block else "") + "</div>" if options.mac_code_block else ""
            highlighted_code = highlight_code("\n".join(code_lines), normalized_language)
            output.append(f'<pre class="hljs code__pre" style="{styles["pre"]}">{header}<code class="language-{html.escape(normalized_language, quote=True)}">{highlighted_code}</code></pre>')
            i += 1
            continue
        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            alt, src = image_match.groups()
            images.append({"source": src, "resolvedPath": str((source_path.parent / src).resolve()) if not re.match(r"https?://", src) else src, "alt": alt})
            output.append(f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" style="{styles["img"]}" />')
            i += 1
            continue
        heading = re.fullmatch(r"(#{1,6})\s+(.+)", stripped)
        if heading:
            level = min(len(heading.group(1)), 3)
            if not options.keep_title and not first_heading_removed and level <= 2:
                first_heading_removed = True
            else:
                heading_style = styles[f"h{level}"]
                output.append(f'<h{level} style="{heading_style}">{inline(heading.group(2), citations, options.cite)}</h{level}>')
            i += 1
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            output.append(f'<hr style="{styles["hr"]}" />')
            i += 1
            continue
        if stripped.startswith(">"):
            output.append(f'<blockquote style="{styles["blockquote"]}">{inline(stripped[1:].lstrip(), citations, options.cite)}</blockquote>')
            i += 1
            continue
        list_match = re.fullmatch(r"(?:[-*+]|(\d+)[.)])\s+(.+)", stripped)
        if list_match:
            ordered = bool(list_match.group(1))
            tag = "ol" if ordered else "ul"
            items: List[str] = []
            while i < len(lines):
                current = re.fullmatch(r"(?:[-*+]|(\d+)[.)])\s+(.+)", lines[i].strip())
                if not current or bool(current.group(1)) != ordered:
                    break
                items.append(f'<li style="{styles["li"]}">{inline(current.group(2), citations, options.cite)}</li>')
                i += 1
            output.append(f'<{tag} style="{styles[tag]}">' + "".join(items) + f'</{tag}>')
            continue
        if "|" in stripped and i + 1 < len(lines) and re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", lines[i + 1]):
            headers = [cell.strip() for cell in stripped.strip("|").split("|")]
            i += 2
            rows: List[List[str]] = []
            while i < len(lines) and "|" in lines[i]:
                rows.append([cell.strip() for cell in lines[i].strip().strip("|").split("|")])
                i += 1
            header_html = "".join(f'<th style="{styles["th"]}">{inline(cell, citations, options.cite)}</th>' for cell in headers)
            row_html = "".join("<tr>" + "".join(f'<td style="{styles["td"]}">{inline(cell, citations, options.cite)}</td>' for cell in row) + "</tr>" for row in rows)
            output.append(f'<table style="{styles["table"]}"><thead><tr>{header_html}</tr></thead><tbody>{row_html}</tbody></table>')
            continue
        output.append(f'<p style="{styles["p"]}">{inline(stripped, citations, options.cite)}</p>')
        i += 1

    if citations:
        citation_items = "".join(f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>: {html.escape(url)}</li>' for label, url in citations)
        output.append(f'<h3 style="{styles["h3"]}">参考链接</h3><ol style="{styles["ol"]}">{citation_items}</ol>')
    content_html = f'<section style="{styles["article"]}">' + "".join(output) + "</section>"
    document = "<!doctype html><html><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
    document += f"<title>{html.escape(title)}</title></head><body>{content_html}</body></html>"
    return RenderResult(title, summary, author, frontmatter, content_html, document, images, options)


def resolve_asset_path(source: str, source_path: pathlib.Path) -> str:
    if re.match(r"https?://", source):
        return source
    path = pathlib.Path(source).expanduser()
    if not path.is_absolute():
        path = source_path.parent / path
    return str(path.resolve())


def build_manifest(result: RenderResult, source_path: pathlib.Path, html_path: pathlib.Path) -> Dict[str, object]:
    cover_source = next(
        (
            result.frontmatter[key]
            for key in ("coverimage", "featureimage", "cover", "image")
            if result.frontmatter.get(key)
        ),
        "",
    )
    cover = (
        {"source": cover_source, "resolvedPath": resolve_asset_path(cover_source, source_path)}
        if cover_source
        else None
    )
    return {
        "schemaVersion": 1,
        "htmlPath": str(html_path),
        "assetBaseDir": str(source_path.parent.resolve()),
        "title": result.title,
        "summary": result.summary,
        "author": result.author,
        "cover": cover,
        "contentImages": result.content_images,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Markdown as WeChat-friendly HTML")
    parser.add_argument("markdown_file")
    parser.add_argument("--output")
    parser.add_argument("--theme")
    parser.add_argument("--color")
    parser.add_argument("--font-family")
    parser.add_argument("--font-size")
    parser.add_argument("--code-theme")
    parser.add_argument("--no-mac-code-block", action="store_true")
    cite_group = parser.add_mutually_exclusive_group()
    cite_group.add_argument("--cite", action="store_true", dest="cite", default=None)
    cite_group.add_argument("--no-cite", action="store_false", dest="cite")
    parser.add_argument("--keep-title", action="store_true", default=None)
    parser.add_argument("--manifest", help="Write a renderer-to-publisher manifest JSON file")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    source = pathlib.Path(args.markdown_file).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise ValueError("markdown_file must be an existing .md file")
    overrides = {"theme": args.theme, "color": args.color, "font_family": args.font_family, "font_size": args.font_size, "code_theme": args.code_theme, "cite": args.cite, "keep_title": args.keep_title}
    if args.no_mac_code_block:
        overrides["mac_code_block"] = False
    options = resolve_options(load_config(), **overrides)
    result = render_markdown(source.read_text("utf-8"), source, options)
    output_path = pathlib.Path(args.output).expanduser().resolve() if args.output else source.with_suffix(".html")
    manifest_path = pathlib.Path(args.manifest).expanduser().resolve() if args.manifest else None
    manifest = build_manifest(result, source, output_path)
    if not args.dry_run:
        output_path.write_text(result.html, "utf-8")
        if manifest_path:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    payload = {"success": True, **manifest, "manifestPath": str(manifest_path) if manifest_path else None, "theme": options.theme, "color": options.color, "codeTheme": options.code_theme, "dryRun": args.dry_run}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else str(output_path))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
