#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
UPLOAD_BODY_IMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
UPLOAD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"

BODY_IMAGE_MAX_SIZE = 1024 * 1024
DEFAULT_THEME = "default"
DEFAULT_COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "vermilion": "#dc2626",
    "yellow": "#ca8a04",
    "purple": "#7c3aed",
    "sky": "#0284c7",
    "rose": "#e11d48",
    "olive": "#708238",
    "black": "#111827",
    "gray": "#4b5563",
    "pink": "#db2777",
    "red": "#dc2626",
    "orange": "#ea580c",
    "teal": "#2dd4bf",
}
IMAGE_MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".svg": "image/svg+xml",
}
BODY_UPLOAD_ALLOWED_MIME = {"image/jpeg", "image/png"}


class WechatError(RuntimeError):
    pass


@dataclass
class Account:
    name: str = ""
    alias: str = ""
    default: bool = False
    default_author: str = ""
    need_open_comment: Optional[int] = None
    only_fans_can_comment: Optional[int] = None
    app_id: str = ""
    app_secret: str = ""


@dataclass
class Config:
    default_theme: str = DEFAULT_THEME
    default_color: str = ""
    default_author: str = ""
    need_open_comment: int = 1
    only_fans_can_comment: int = 0
    accounts: List[Account] = field(default_factory=list)
    source_path: str = ""


@dataclass
class RenderResult:
    title: str
    summary: str
    author: str
    html_content: str
    html_path: str
    frontmatter: Dict[str, Any]
    inline_images: List[str]
    source_path: str
    base_dir: str


@dataclass
class UploadAsset:
    data: bytes
    filename: str
    content_type: str
    source: str
    temp_path: Optional[str] = None


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def bool01(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    text = str(value).strip().lower()
    return 1 if text in {"1", "true", "yes", "y", "on"} else 0


def sanitize_slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or "wechat-post"


def truncate_summary(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", strip_html(text)).strip()
    if len(text) <= limit:
        return text
    truncated = text[: limit - 3]
    last_punct = max(truncated.rfind("。"), truncated.rfind("，"), truncated.rfind(";"), truncated.rfind("；"))
    if last_punct > 80:
        return truncated[: last_punct + 1]
    return truncated.rstrip() + "..."


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def parse_env_file(path: pathlib.Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    result: Dict[str, str] = {}
    for raw in path.read_text("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = strip_quotes(value.strip())
    return result


def parse_extend_config(content: str, source_path: str = "") -> Config:
    config = Config(source_path=source_path)
    accounts: List[Dict[str, str]] = []
    current: Optional[Dict[str, str]] = None
    in_accounts = False

    def flush_current() -> None:
        nonlocal current
        if current is not None:
            accounts.append(current)
            current = None

    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if line == "accounts:":
            in_accounts = True
            continue

        if in_accounts:
            list_match = re.match(r"^\s*-\s+(.+)$", raw)
            if list_match:
                flush_current()
                current = {}
                payload = list_match.group(1)
                if ":" in payload:
                    key, value = payload.split(":", 1)
                    current[key.strip()] = strip_quotes(value.strip())
                continue

            if current is not None and re.match(r"^\s{2,}", raw) and ":" in line:
                key, value = line.split(":", 1)
                current[key.strip()] = strip_quotes(value.strip())
                continue

            if not raw.startswith(" "):
                flush_current()
                in_accounts = False
            else:
                continue

        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = strip_quotes(value.strip())
        if value in {"", "null", "None"}:
            continue
        if key == "default_theme":
            config.default_theme = value
        elif key == "default_color":
            config.default_color = value
        elif key == "default_author":
            config.default_author = value
        elif key == "need_open_comment":
            config.need_open_comment = bool01(value, 1)
        elif key == "only_fans_can_comment":
            config.only_fans_can_comment = bool01(value, 0)

    flush_current()
    for raw_account in accounts:
        config.accounts.append(
            Account(
                name=raw_account.get("name", ""),
                alias=raw_account.get("alias", ""),
                default=bool(raw_account.get("default", "").lower() in {"1", "true", "yes"}),
                default_author=raw_account.get("default_author", ""),
                need_open_comment=bool01(raw_account["need_open_comment"], 1)
                if "need_open_comment" in raw_account
                else None,
                only_fans_can_comment=bool01(raw_account["only_fans_can_comment"], 0)
                if "only_fans_can_comment" in raw_account
                else None,
                app_id=raw_account.get("app_id", ""),
                app_secret=raw_account.get("app_secret", ""),
            )
        )
    return config


def config_paths() -> List[pathlib.Path]:
    home = pathlib.Path.home()
    xdg = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
    return [
        pathlib.Path.cwd() / ".guige-skills" / "guige-to-wechat" / "EXTEND.md",
        xdg / "guige-skills" / "guige-to-wechat" / "EXTEND.md",
        home / ".guige-skills" / "guige-to-wechat" / "EXTEND.md",
        pathlib.Path.cwd() / ".baoyu-skills" / "baoyu-post-to-wechat" / "EXTEND.md",
        xdg / "baoyu-skills" / "baoyu-post-to-wechat" / "EXTEND.md",
        home / ".baoyu-skills" / "baoyu-post-to-wechat" / "EXTEND.md",
    ]


def load_config() -> Config:
    for path in config_paths():
        if path.exists():
            return parse_extend_config(path.read_text("utf-8"), str(path))
    return Config()


def resolve_account(config: Config, alias: str = "") -> Account:
    if not config.accounts:
        return Account(
            default_author=config.default_author,
            need_open_comment=config.need_open_comment,
            only_fans_can_comment=config.only_fans_can_comment,
        )
    selected: Optional[Account] = None
    if alias:
        selected = next((account for account in config.accounts if account.alias == alias), None)
        if selected is None:
            raise WechatError(f"Account alias not found in EXTEND.md: {alias}")
    elif len(config.accounts) == 1:
        selected = config.accounts[0]
    else:
        selected = next((account for account in config.accounts if account.default), None)
    if selected is None:
        aliases = ", ".join(account.alias for account in config.accounts if account.alias)
        raise WechatError(f"Multiple accounts configured. Pass --account <alias>. Available: {aliases}")
    return Account(
        name=selected.name,
        alias=selected.alias,
        default=selected.default,
        default_author=selected.default_author or config.default_author,
        need_open_comment=selected.need_open_comment
        if selected.need_open_comment is not None
        else config.need_open_comment,
        only_fans_can_comment=selected.only_fans_can_comment
        if selected.only_fans_can_comment is not None
        else config.only_fans_can_comment,
        app_id=selected.app_id,
        app_secret=selected.app_secret,
    )


def alias_env_prefix(alias: str) -> str:
    return "WECHAT_" + alias.upper().replace("-", "_") + "_"


def load_credentials(account: Account) -> Tuple[str, str, str, List[str]]:
    cwd_env = parse_env_file(pathlib.Path.cwd() / ".guige-skills" / ".env")
    home_env = parse_env_file(pathlib.Path.home() / ".guige-skills" / ".env")
    legacy_cwd_env = parse_env_file(pathlib.Path.cwd() / ".baoyu-skills" / ".env")
    legacy_home_env = parse_env_file(pathlib.Path.home() / ".baoyu-skills" / ".env")
    sources: List[Tuple[str, Dict[str, str], str, str]] = []
    skipped: List[str] = []

    if account.app_id or account.app_secret:
        source = f'EXTEND.md account "{account.alias}"' if account.alias else "EXTEND.md account"
        sources.append((source, {"app_id": account.app_id, "app_secret": account.app_secret}, "app_id", "app_secret"))

    if account.alias:
        prefix = alias_env_prefix(account.alias)
        sources.extend(
            [
                (f"process.env ({prefix}APP_ID)", dict(os.environ), f"{prefix}APP_ID", f"{prefix}APP_SECRET"),
                (f"<cwd>/.guige-skills/.env ({prefix}APP_ID)", cwd_env, f"{prefix}APP_ID", f"{prefix}APP_SECRET"),
                (f"~/.guige-skills/.env ({prefix}APP_ID)", home_env, f"{prefix}APP_ID", f"{prefix}APP_SECRET"),
            ]
        )

    sources.extend(
        [
            ("process.env", dict(os.environ), "WECHAT_APP_ID", "WECHAT_APP_SECRET"),
            ("<cwd>/.guige-skills/.env", cwd_env, "WECHAT_APP_ID", "WECHAT_APP_SECRET"),
            ("~/.guige-skills/.env", home_env, "WECHAT_APP_ID", "WECHAT_APP_SECRET"),
            ("<cwd>/.baoyu-skills/.env", legacy_cwd_env, "WECHAT_APP_ID", "WECHAT_APP_SECRET"),
            ("~/.baoyu-skills/.env", legacy_home_env, "WECHAT_APP_ID", "WECHAT_APP_SECRET"),
        ]
    )

    for name, values, app_key, secret_key in sources:
        app_id = values.get(app_key, "").strip()
        app_secret = values.get(secret_key, "").strip()
        if app_id and app_secret:
            return app_id, app_secret, name, skipped
        if app_id or app_secret:
            missing = app_key if not app_id else secret_key
            skipped.append(f"{name} missing {missing}")

    hint = f" for account {account.alias}" if account.alias else ""
    raise WechatError(
        f"Missing WECHAT_APP_ID or WECHAT_APP_SECRET{hint}. "
        "Set env vars, .guige-skills/.env, or EXTEND.md account credentials."
    )


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    match = re.match(r"^\s*---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$", content)
    if not match:
        return {}, content
    frontmatter: Dict[str, Any] = {}
    current_key = ""
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if re.match(r"^\s+-\s+", raw) and current_key:
            frontmatter.setdefault(current_key, []).append(strip_quotes(raw.strip()[2:].strip()))
            continue
        if ":" in raw:
            key, value = raw.split(":", 1)
            current_key = key.strip()
            value = strip_quotes(value.strip())
            frontmatter[current_key] = [] if value == "" else value
    return frontmatter, match.group(2)


def serialize_frontmatter(frontmatter: Dict[str, Any]) -> str:
    if not frontmatter:
        return ""
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def extract_title_from_markdown(body: str) -> str:
    match = re.search(r"^\s*#{1,2}\s+(.+?)\s*$", body, flags=re.MULTILINE)
    return strip_markdown_inline(match.group(1)).strip() if match else ""


def extract_summary_from_markdown(body: str, limit: int = 120) -> str:
    cleaned = re.sub(r"```[\s\S]*?```", "", body)
    for block in re.split(r"\n\s*\n", cleaned):
        text = block.strip()
        if not text or text.startswith("#") or text.startswith("!") or text.startswith("|"):
            continue
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
        text = strip_markdown_inline(text)
        if text:
            return truncate_summary(text, limit)
    return ""


def strip_markdown_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def resolve_color(color: str = "") -> str:
    if not color:
        return DEFAULT_COLORS["blue"]
    color = color.strip()
    if re.match(r"^#[0-9a-fA-F]{6}$", color):
        return color
    return DEFAULT_COLORS.get(color.lower(), color)


def theme_styles(theme: str, color: str) -> Dict[str, str]:
    primary = resolve_color(color)
    base = {
        "article": "font-size:16px;line-height:1.85;color:#1f2937;",
        "h1": f"font-size:24px;line-height:1.35;font-weight:700;color:#111827;border-bottom:3px solid {primary};padding-bottom:0.35em;margin:1.2em 0 0.8em;",
        "h2": f"font-size:21px;line-height:1.4;font-weight:700;color:#111827;border-left:5px solid {primary};padding-left:0.65em;margin:1.8em 0 0.8em;",
        "h3": f"font-size:18px;font-weight:700;color:{primary};margin:1.5em 0 0.7em;",
        "p": "margin:0.9em 0;",
        "blockquote": f"border-left:4px solid {primary};background:#f8fafc;color:#475569;padding:0.8em 1em;margin:1.2em 0;",
        "code": "font-family:Menlo,Consolas,monospace;background:#f3f4f6;border-radius:4px;padding:0.1em 0.35em;",
        "pre": "font-family:Menlo,Consolas,monospace;background:#111827;color:#f9fafb;border-radius:8px;padding:1em;overflow-x:auto;line-height:1.6;",
        "img": "display:block;width:100%;height:auto;margin:1.5em auto;border-radius:8px;",
        "hr": f"border:none;border-top:1px solid {primary};opacity:0.35;margin:2em 0;",
        "table": "width:100%;border-collapse:collapse;margin:1.2em 0;font-size:14px;",
        "th": f"border:1px solid #e5e7eb;background:{primary};color:#fff;padding:0.55em;",
        "td": "border:1px solid #e5e7eb;padding:0.55em;",
    }
    if theme == "simple":
        base["h1"] = f"font-size:24px;font-weight:700;color:{primary};margin:1.2em 0 0.8em;"
        base["h2"] = f"font-size:20px;font-weight:700;color:#111827;margin:1.8em 0 0.8em;"
    elif theme == "grace":
        base["article"] = "font-size:16px;line-height:1.9;color:#374151;"
        base["blockquote"] = f"border-left:0;background:#fff7ed;color:#57534e;padding:1em;margin:1.2em 0;border-radius:8px;border-top:2px solid {primary};"
    elif theme == "modern":
        base["article"] = "font-size:16px;line-height:1.85;color:#d1d5db;background:#07090f;padding:1em;border-radius:12px;"
        base["h1"] = f"font-size:24px;color:#f9fafb;border-bottom:3px solid {primary};padding-bottom:0.35em;"
        base["h2"] = f"font-size:21px;color:#f9fafb;border-left:5px solid {primary};padding-left:0.65em;"
        base["h3"] = f"font-size:18px;color:{primary};"
        base["p"] = "margin:0.9em 0;color:#d1d5db;"
        base["blockquote"] = "border-left:4px solid #f59e0b;background:#111827;color:#e5e7eb;padding:0.8em 1em;margin:1.2em 0;"
    return base


class MarkdownRenderer:
    def __init__(self, theme: str = DEFAULT_THEME, color: str = "", cite: bool = True) -> None:
        self.styles = theme_styles(theme, color)
        self.cite = cite
        self.citations: List[Tuple[str, str]] = []
        self.inline_images: List[str] = []

    def render(self, markdown: str) -> str:
        lines = markdown.replace("\r\n", "\n").split("\n")
        output: List[str] = []
        paragraph: List[str] = []
        list_items: List[str] = []
        list_type = ""
        in_code = False
        code_lines: List[str] = []
        table_lines: List[str] = []

        def flush_paragraph() -> None:
            nonlocal paragraph
            if paragraph:
                text = " ".join(line.strip() for line in paragraph).strip()
                if text:
                    output.append(f'<p style="{self.styles["p"]}">{self.inline(text)}</p>')
                paragraph = []

        def flush_list() -> None:
            nonlocal list_items, list_type
            if list_items:
                tag = "ol" if list_type == "ol" else "ul"
                output.append(f"<{tag}>" + "".join(list_items) + f"</{tag}>")
                list_items = []
                list_type = ""

        def flush_table() -> None:
            nonlocal table_lines
            if table_lines:
                output.append(self.render_table(table_lines))
                table_lines = []

        for raw in lines:
            line = raw.rstrip()
            if line.strip().startswith("```"):
                flush_paragraph()
                flush_list()
                flush_table()
                if in_code:
                    code = html.escape("\n".join(code_lines))
                    output.append(f'<pre style="{self.styles["pre"]}"><code>{code}</code></pre>')
                    code_lines = []
                    in_code = False
                else:
                    in_code = True
                    code_lines = []
                continue
            if in_code:
                code_lines.append(line)
                continue

            if not line.strip():
                flush_paragraph()
                flush_list()
                flush_table()
                continue

            if self.is_table_line(line):
                flush_paragraph()
                flush_list()
                table_lines.append(line)
                continue
            flush_table()

            if re.match(r"^\s*[-*_]{3,}\s*$", line):
                flush_paragraph()
                flush_list()
                output.append(f'<hr style="{self.styles["hr"]}">')
                continue

            img_match = re.match(r"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
            if img_match:
                flush_paragraph()
                flush_list()
                output.append(self.render_image(img_match.group(2), img_match.group(1)))
                continue

            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                flush_paragraph()
                flush_list()
                level = min(len(heading.group(1)), 3)
                tag = f"h{level}"
                output.append(f'<{tag} style="{self.styles[tag]}">{self.inline(heading.group(2))}</{tag}>')
                continue

            quote = re.match(r"^\s*>\s?(.*)$", line)
            if quote:
                flush_paragraph()
                flush_list()
                output.append(f'<blockquote style="{self.styles["blockquote"]}">{self.inline(quote.group(1))}</blockquote>')
                continue

            unordered = re.match(r"^\s*[-*+]\s+(.+)$", line)
            ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
            if unordered or ordered:
                flush_paragraph()
                wanted = "ol" if ordered else "ul"
                if list_type and list_type != wanted:
                    flush_list()
                list_type = wanted
                item_text = (ordered or unordered).group(1)
                list_items.append(f"<li>{self.inline(item_text)}</li>")
                continue

            paragraph.append(line)

        flush_paragraph()
        flush_list()
        flush_table()
        if in_code:
            code = html.escape("\n".join(code_lines))
            output.append(f'<pre style="{self.styles["pre"]}"><code>{code}</code></pre>')

        if self.citations and self.cite:
            output.append(self.render_citations())
        return f'<section style="{self.styles["article"]}">\n' + "\n".join(output) + "\n</section>"

    def is_table_line(self, line: str) -> bool:
        return "|" in line and line.strip().startswith("|") and line.strip().endswith("|")

    def render_table(self, lines: List[str]) -> str:
        rows = []
        for line in lines:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(re.match(r"^:?-{3,}:?$", cell) for cell in cells):
                continue
            rows.append(cells)
        if not rows:
            return ""
        html_rows = []
        for idx, cells in enumerate(rows):
            tag = "th" if idx == 0 else "td"
            cell_style = self.styles["th"] if idx == 0 else self.styles["td"]
            html_cells = "".join(f'<{tag} style="{cell_style}">{self.inline(cell)}</{tag}>' for cell in cells)
            html_rows.append(f"<tr>{html_cells}</tr>")
        return f'<table style="{self.styles["table"]}"><tbody>' + "".join(html_rows) + "</tbody></table>"

    def render_image(self, src: str, alt: str = "") -> str:
        src = strip_quotes(src.strip())
        alt = html.escape(alt.strip(), quote=True)
        self.inline_images.append(src)
        return f'<img src="{html.escape(src, quote=True)}" alt="{alt}" style="{self.styles["img"]}">'

    def inline(self, text: str) -> str:
        escaped = html.escape(text, quote=False)
        escaped = re.sub(r"`([^`]+)`", lambda m: f'<code style="{self.styles["code"]}">{m.group(1)}</code>', escaped)
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)

        def replace_link(match: re.Match[str]) -> str:
            label = match.group(1)
            url = html.unescape(match.group(2)).strip()
            if self.cite and re.match(r"^https?://", url):
                idx = len(self.citations) + 1
                self.citations.append((html.unescape(label), url))
                return f"{label}<sup>[{idx}]</sup>"
            return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

        escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, escaped)
        return escaped

    def render_citations(self) -> str:
        items = []
        for idx, (label, url) in enumerate(self.citations, 1):
            items.append(
                f'<li style="margin:0.35em 0;">[{idx}] {html.escape(label)}: '
                f'{html.escape(url)}</li>'
            )
        return (
            f'<section style="margin-top:2em;padding-top:1em;border-top:1px solid #e5e7eb;">'
            f'<h3 style="{self.styles["h3"]}">参考链接</h3><ol>'
            + "".join(items)
            + "</ol></section>"
        )


def extract_html_body(content: str) -> str:
    output_match = re.search(r'<div\s+id=["\']output["\'][^>]*>([\s\S]*?)</div>\s*</body>', content, flags=re.I)
    if output_match:
        return output_match.group(1).strip()
    body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", content, flags=re.I)
    return body_match.group(1).strip() if body_match else content


def extract_html_title(content: str) -> str:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, flags=re.I | re.S)
    if title_match:
        return strip_html(title_match.group(1)).strip()
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, flags=re.I | re.S)
    return strip_html(h1_match.group(1)).strip() if h1_match else ""


def save_plain_text_as_markdown(text: str, title: str = "") -> pathlib.Path:
    today = _dt.date.today().isoformat()
    slug_source = title or text[:40]
    slug = sanitize_slug(slug_source)
    out_dir = pathlib.Path.cwd() / "post-to-wechat" / today
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.md"
    body = f"# {title}\n\n{text.strip()}\n" if title else text.strip() + "\n"
    path.write_text(body, "utf-8")
    return path


def resolve_input(input_value: str, title: str = "") -> pathlib.Path:
    candidate = pathlib.Path(input_value).expanduser()
    if candidate.exists():
        return candidate.resolve()
    return save_plain_text_as_markdown(input_value, title).resolve()


def render_input(
    input_path: pathlib.Path,
    args: argparse.Namespace,
    config: Config,
    account: Account,
) -> RenderResult:
    content = input_path.read_text("utf-8")
    base_dir = str(input_path.parent)
    frontmatter: Dict[str, Any] = {}
    inline_images: List[str] = []
    theme = args.theme or config.default_theme or DEFAULT_THEME
    color = args.color or config.default_color

    if input_path.suffix.lower() == ".html":
        html_content = extract_html_body(content)
        title = args.title or extract_html_title(content) or input_path.stem
        summary = args.summary or truncate_summary(html_content)
        author = args.author or account.default_author or config.default_author
    else:
        frontmatter, body = parse_frontmatter(content)
        title = args.title or str(frontmatter.get("title") or "") or extract_title_from_markdown(body) or input_path.stem
        summary = (
            args.summary
            or str(frontmatter.get("digest") or frontmatter.get("summary") or frontmatter.get("description") or "")
            or extract_summary_from_markdown(body)
        )
        author = args.author or str(frontmatter.get("author") or "") or account.default_author or config.default_author
        renderer = MarkdownRenderer(theme=theme, color=color, cite=not args.no_cite)
        html_content = renderer.render(body)
        inline_images = renderer.inline_images

    html_path = resolve_html_path(input_path, args.output_html)
    pathlib.Path(html_path).write_text(wrap_debug_html(title, html_content), "utf-8")
    return RenderResult(
        title=title,
        summary=truncate_summary(summary),
        author=author,
        html_content=html_content,
        html_path=html_path,
        frontmatter=frontmatter,
        inline_images=inline_images,
        source_path=str(input_path),
        base_dir=base_dir,
    )


def resolve_html_path(input_path: pathlib.Path, output_html: str = "") -> str:
    if output_html:
        path = pathlib.Path(output_html).expanduser().resolve()
    else:
        path = input_path.with_suffix(".wechat.html")
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def wrap_debug_html(title: str, body: str) -> str:
    return (
        "<!doctype html>\n<html><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title></head><body><div id=\"output\">\n"
        f"{body}\n</div></body></html>\n"
    )


def infer_content_type(filename: str, data: bytes) -> Tuple[str, str]:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"
    if data.startswith(b"\x89PNG"):
        return "image/png", ".png"
    if data[:4] == b"GIF8":
        return "image/gif", ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", ".webp"
    ext = pathlib.Path(filename).suffix.lower()
    return IMAGE_MIME_BY_EXT.get(ext) or mimetypes.guess_type(filename)[0] or "application/octet-stream", ext


def download_url(url: str) -> UploadAsset:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
        final_url = response.geturl()
        filename = pathlib.PurePosixPath(urllib.parse.urlparse(final_url).path).name or "image.jpg"
        content_type = (response.headers.get("content-type") or "").split(";")[0].strip()
    detected_type, ext = infer_content_type(filename, data)
    content_type = content_type or detected_type
    if pathlib.Path(filename).suffix == "" and ext:
        filename += ext
    return UploadAsset(data=data, filename=filename, content_type=content_type, source=url)


def load_asset(path_or_url: str, base_dir: str = "") -> UploadAsset:
    if re.match(r"^https?://", path_or_url):
        return download_url(path_or_url)
    path = pathlib.Path(path_or_url).expanduser()
    if not path.is_absolute():
        path = pathlib.Path(base_dir or os.getcwd()) / path
    path = path.resolve()
    if not path.exists():
        raise WechatError(f"Image not found: {path}")
    data = path.read_bytes()
    content_type, ext = infer_content_type(path.name, data)
    filename = path.name if pathlib.Path(path.name).suffix else path.name + ext
    return UploadAsset(data=data, filename=filename, content_type=content_type, source=str(path), temp_path=str(path))


def make_temp_asset(data: bytes, filename: str, content_type: str, source: str) -> UploadAsset:
    tmp_dir = tempfile.mkdtemp(prefix="guige-to-wechat-")
    path = pathlib.Path(tmp_dir) / filename
    path.write_bytes(data)
    return UploadAsset(data=data, filename=filename, content_type=content_type, source=source, temp_path=str(path))


def run_conversion_tool(asset: UploadAsset) -> Optional[UploadAsset]:
    if not asset.temp_path:
        asset = make_temp_asset(asset.data, asset.filename, asset.content_type, asset.source)
    src = pathlib.Path(asset.temp_path)
    tools = []
    if shutil.which("sips"):
        tools.append("sips")
    if shutil.which("cwebp"):
        tools.append("cwebp")
    if not tools:
        return None

    widths = [2560, 2048, 1600, 1280, 1024, 800, 640]
    for width in widths:
        out = src.with_name(f"{src.stem}-{width}.jpg")
        if "sips" in tools:
            cmd = ["sips", "-s", "format", "jpeg", "-Z", str(width), str(src), "--out", str(out)]
        else:
            out = src.with_name(f"{src.stem}-{width}.jpg")
            cmd = ["cwebp", "-q", "82", "-resize", str(width), "0", str(src), "-o", str(out)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and out.exists() and out.stat().st_size <= BODY_IMAGE_MAX_SIZE:
            data = out.read_bytes()
            return UploadAsset(data=data, filename=out.name, content_type="image/jpeg", source=asset.source, temp_path=str(out))
    return None


def prepare_body_asset(asset: UploadAsset) -> UploadAsset:
    if asset.content_type in BODY_UPLOAD_ALLOWED_MIME and len(asset.data) <= BODY_IMAGE_MAX_SIZE:
        return asset
    converted = run_conversion_tool(asset)
    if converted:
        eprint(f"[guige-to-wechat] Converted body image: {asset.filename} -> {converted.filename}")
        return converted
    eprint(f"[guige-to-wechat] Warning: body image may be rejected by WeChat: {asset.filename}")
    return asset


def build_multipart(field: str, asset: UploadAsset) -> Tuple[bytes, str]:
    boundary = "----GuigeWechatBoundary" + _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{asset.filename}"\r\n'
        f"Content-Type: {asset.content_type}\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return header + asset.data + footer, boundary


def http_json(url: str, method: str = "GET", data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Any:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        raise WechatError(f"HTTP {error.code}: {raw[:500]}") from error
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise WechatError(f"Invalid JSON response: {raw[:500]}") from error


def fetch_access_token(app_id: str, app_secret: str) -> str:
    query = urllib.parse.urlencode({"grant_type": "client_credential", "appid": app_id, "secret": app_secret})
    data = http_json(f"{TOKEN_URL}?{query}")
    if data.get("errcode"):
        raise WechatError(f"Access token error {data.get('errcode')}: {data.get('errmsg')}")
    token = data.get("access_token")
    if not token:
        raise WechatError(f"No access_token in response: {data}")
    return token


def upload_to_wechat(asset: UploadAsset, access_token: str, upload_type: str) -> Dict[str, Any]:
    if upload_type == "body":
        url = f"{UPLOAD_BODY_IMG_URL}?access_token={urllib.parse.quote(access_token)}"
        asset = prepare_body_asset(asset)
    else:
        url = f"{UPLOAD_MATERIAL_URL}?type=image&access_token={urllib.parse.quote(access_token)}"
    body, boundary = build_multipart("media", asset)
    data = http_json(url, method="POST", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    if data.get("errcode"):
        raise WechatError(f"Upload failed {data.get('errcode')}: {data.get('errmsg')}")
    return data


def to_https(url: str) -> str:
    return re.sub(r"^http://", "https://", url)


def upload_image(asset_source: str, access_token: str, base_dir: str, upload_type: str) -> Dict[str, Any]:
    asset = load_asset(asset_source, base_dir)
    response = upload_to_wechat(asset, access_token, upload_type)
    if upload_type == "body":
        return {"url": to_https(response.get("url", "")), "media_id": ""}
    response["url"] = to_https(response.get("url", ""))
    return response


IMG_TAG_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)


def replace_img_src(tag: str, new_src: str) -> str:
    if re.search(r"\sdata-local-path=[\"'][^\"']+[\"']", tag):
        tag = re.sub(r"\sdata-local-path=[\"'][^\"']+[\"']", "", tag)
    return re.sub(r'\ssrc=["\'][^"\']+["\']', f' src="{html.escape(new_src, quote=True)}"', tag, count=1)


def upload_images_in_html(
    html_content: str,
    access_token: str,
    base_dir: str,
    article_type: str,
    collect_cover_fallback: bool,
) -> Tuple[str, str, List[str]]:
    uploaded: Dict[str, Dict[str, Any]] = {}
    first_cover_media_id = ""
    image_media_ids: List[str] = []
    result = html_content

    for match in list(IMG_TAG_RE.finditer(html_content)):
        full_tag, src = match.group(0), match.group(1)
        if src.startswith("https://mmbiz.qpic.cn"):
            continue
        local_match = re.search(r'data-local-path=["\']([^"\']+)["\']', full_tag)
        image_source = local_match.group(1) if local_match else src
        try:
            body_resp = uploaded.get(image_source)
            if not body_resp:
                eprint(f"[guige-to-wechat] Uploading body image: {image_source}")
                body_resp = upload_image(image_source, access_token, base_dir, "body")
                uploaded[image_source] = body_resp
            new_tag = replace_img_src(full_tag, body_resp["url"])
            result = result.replace(full_tag, new_tag)

            if article_type == "newspic" or (collect_cover_fallback and not first_cover_media_id):
                material_key = image_source + ":material"
                material_resp = uploaded.get(material_key)
                if not material_resp:
                    material_resp = upload_image(image_source, access_token, base_dir, "material")
                    uploaded[material_key] = material_resp
                if article_type == "newspic" and material_resp.get("media_id"):
                    image_media_ids.append(material_resp["media_id"])
                if collect_cover_fallback and not first_cover_media_id and material_resp.get("media_id"):
                    first_cover_media_id = material_resp["media_id"]
        except Exception as error:
            eprint(f"[guige-to-wechat] Failed to upload image {image_source}: {error}")
    return result, first_cover_media_id, image_media_ids


def resolve_cover(rendered: RenderResult, args: argparse.Namespace) -> str:
    fm = rendered.frontmatter
    raw = args.cover or fm.get("coverImage") or fm.get("featureImage") or fm.get("cover") or fm.get("image")
    if raw:
        return str(raw)
    candidate = pathlib.Path(rendered.base_dir) / "imgs" / "cover.png"
    if candidate.exists():
        return str(candidate)
    return rendered.inline_images[0] if rendered.inline_images else ""


def html_has_image(html_content: str) -> bool:
    return bool(IMG_TAG_RE.search(html_content))


def validate_article_inputs(rendered: RenderResult, article_type: str, cover: str) -> None:
    has_image_candidate = bool(rendered.inline_images) or html_has_image(rendered.html_content)
    if article_type == "news" and not cover and not has_image_candidate:
        raise WechatError("news requires a cover image or at least one inline image for cover fallback.")
    if article_type == "newspic" and not has_image_candidate:
        raise WechatError("newspic requires at least one inline image.")


def build_draft_article(
    title: str,
    author: str,
    digest: str,
    content: str,
    thumb_media_id: str,
    article_type: str,
    image_media_ids: List[str],
    need_open_comment: int,
    only_fans_can_comment: int,
) -> Dict[str, Any]:
    if article_type == "newspic":
        if not image_media_ids:
            raise WechatError("newspic requires at least one inline image.")
        article: Dict[str, Any] = {
            "article_type": "newspic",
            "title": title,
            "content": content,
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment,
            "image_info": {"image_list": [{"image_media_id": mid} for mid in image_media_ids]},
        }
    else:
        if not thumb_media_id:
            raise WechatError("news requires a cover image.")
        article = {
            "article_type": "news",
            "title": title,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment,
        }
        if digest:
            article["digest"] = digest
    if author:
        article["author"] = author
    return article


def publish_to_draft(
    access_token: str,
    title: str,
    author: str,
    digest: str,
    content: str,
    thumb_media_id: str,
    article_type: str,
    image_media_ids: List[str],
    need_open_comment: int,
    only_fans_can_comment: int,
) -> Dict[str, Any]:
    article = build_draft_article(
        title=title,
        author=author,
        digest=digest,
        content=content,
        thumb_media_id=thumb_media_id,
        article_type=article_type,
        image_media_ids=image_media_ids,
        need_open_comment=need_open_comment,
        only_fans_can_comment=only_fans_can_comment,
    )

    url = f"{DRAFT_URL}?access_token={urllib.parse.quote(access_token)}"
    body = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
    data = http_json(url, method="POST", data=body, headers={"Content-Type": "application/json"})
    if data.get("errcode"):
        raise WechatError(f"Publish failed {data.get('errcode')}: {data.get('errmsg')}")
    return data


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish Markdown/HTML/plain text to WeChat Official Account drafts.")
    parser.add_argument("input", nargs="?", help="Markdown file, HTML file, or plain text")
    parser.add_argument("--type", choices=["news", "newspic"], default="news")
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--summary")
    parser.add_argument("--cover")
    parser.add_argument("--theme")
    parser.add_argument("--color")
    parser.add_argument("--account")
    parser.add_argument("--no-cite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-html", default="")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.input:
        raise WechatError("Missing input. Pass a Markdown/HTML file or plain text.")

    config = load_config()
    account = resolve_account(config, args.account or "")
    input_path = resolve_input(args.input, args.title or "")
    rendered = render_input(input_path, args, config, account)
    cover = resolve_cover(rendered, args)
    validate_article_inputs(rendered, args.type, cover)
    need_open_comment = account.need_open_comment if account.need_open_comment is not None else config.need_open_comment
    only_fans_can_comment = (
        account.only_fans_can_comment
        if account.only_fans_can_comment is not None
        else config.only_fans_can_comment
    )

    eprint(f"[guige-to-wechat] Input: {rendered.source_path}")
    eprint(f"[guige-to-wechat] HTML: {rendered.html_path}")
    eprint(f"[guige-to-wechat] Title: {rendered.title}")
    if rendered.author:
        eprint(f"[guige-to-wechat] Author: {rendered.author}")
    if rendered.summary:
        eprint(f"[guige-to-wechat] Summary: {rendered.summary}")
    if cover:
        eprint(f"[guige-to-wechat] Cover: {cover}")
    elif args.type == "news":
        eprint("[guige-to-wechat] Cover: will try first inline image fallback")

    if args.dry_run:
        result = {
            "success": True,
            "dryRun": True,
            "title": rendered.title,
            "summary": rendered.summary,
            "author": rendered.author,
            "articleType": args.type,
            "htmlPath": rendered.html_path,
            "input": rendered.source_path,
            "cover": cover or None,
            "inlineImages": rendered.inline_images,
            "comments": {
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment,
            },
            "config": config.source_path or None,
            "account": account.alias or None,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else rendered.html_path)
        return 0

    app_id, app_secret, cred_source, skipped = load_credentials(account)
    for item in skipped:
        eprint(f"[guige-to-wechat] Skipped incomplete credential source: {item}")
    eprint(f"[guige-to-wechat] Credentials: {cred_source}")
    eprint("[guige-to-wechat] Fetching access token...")
    access_token = fetch_access_token(app_id, app_secret)

    collect_cover_fallback = args.type == "news" and not cover
    eprint("[guige-to-wechat] Uploading inline images...")
    processed_html, first_cover_media_id, image_media_ids = upload_images_in_html(
        rendered.html_content,
        access_token,
        rendered.base_dir,
        args.type,
        collect_cover_fallback,
    )

    thumb_media_id = ""
    if cover:
        eprint(f"[guige-to-wechat] Uploading cover: {cover}")
        cover_resp = upload_image(cover, access_token, rendered.base_dir, "material")
        thumb_media_id = cover_resp.get("media_id", "")
    elif first_cover_media_id:
        thumb_media_id = first_cover_media_id

    final_html_path = pathlib.Path(rendered.html_path)
    final_html_path.write_text(wrap_debug_html(rendered.title, processed_html), "utf-8")
    eprint("[guige-to-wechat] Publishing draft...")
    response = publish_to_draft(
        access_token=access_token,
        title=rendered.title,
        author=rendered.author,
        digest=rendered.summary,
        content=processed_html,
        thumb_media_id=thumb_media_id,
        article_type=args.type,
        image_media_ids=image_media_ids,
        need_open_comment=need_open_comment,
        only_fans_can_comment=only_fans_can_comment,
    )

    result = {
        "success": True,
        "media_id": response.get("media_id"),
        "title": rendered.title,
        "articleType": args.type,
        "htmlPath": str(final_html_path),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
