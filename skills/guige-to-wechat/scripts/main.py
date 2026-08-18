#!/usr/bin/env python3
"""Publish a renderer manifest to a WeChat Official Account draft."""

from __future__ import annotations

import argparse
import datetime as dt
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
from typing import Any, Dict, List, Optional, Tuple


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
UPLOAD_BODY_IMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
UPLOAD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
BODY_IMAGE_MAX_SIZE = 1024 * 1024
IMAGE_MIME_BY_EXT = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif",
    ".webp": "image/webp", ".bmp": "image/bmp", ".tif": "image/tiff", ".tiff": "image/tiff",
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
    need_open_comment: Optional[int] = None
    only_fans_can_comment: Optional[int] = None
    app_id: str = ""
    app_secret: str = ""


@dataclass
class Config:
    need_open_comment: int = 1
    only_fans_can_comment: int = 0
    accounts: List[Account] = field(default_factory=list)
    source_path: str = ""


@dataclass
class PublicationInput:
    title: str
    summary: str
    author: str
    html_content: str
    html_path: str
    cover_source: str
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
    return value[1:-1] if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'} else value


def bool01(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    return 1 if str(value).strip().lower() in {"1", "true", "yes", "y", "on"} else 0


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def truncate_summary(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", strip_html(text)).strip()
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def parse_env_file(path: pathlib.Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    result: Dict[str, str] = {}
    for raw in path.read_text("utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = strip_quotes(value)
    return result


def parse_extend_config(content: str, source_path: str = "") -> Config:
    config = Config(source_path=source_path)
    accounts: List[Dict[str, str]] = []
    current: Optional[Dict[str, str]] = None
    in_accounts = False
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "accounts:":
            in_accounts = True
            continue
        if in_accounts and re.match(r"^\s*-\s+", raw):
            if current is not None:
                accounts.append(current)
            current = {}
            payload = re.sub(r"^\s*-\s+", "", raw)
            if ":" in payload:
                key, value = payload.split(":", 1)
                current[key.strip()] = strip_quotes(value)
            continue
        if in_accounts and current is not None and re.match(r"^\s{2,}", raw) and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = strip_quotes(value)
            continue
        if in_accounts and not raw.startswith(" "):
            if current is not None:
                accounts.append(current)
                current = None
            in_accounts = False
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() == "need_open_comment":
            config.need_open_comment = bool01(value, 1)
        elif key.strip() == "only_fans_can_comment":
            config.only_fans_can_comment = bool01(value, 0)
    if current is not None:
        accounts.append(current)
    for item in accounts:
        config.accounts.append(Account(
            name=item.get("name", ""), alias=item.get("alias", ""),
            default=item.get("default", "").lower() in {"1", "true", "yes"},
            need_open_comment=bool01(item["need_open_comment"], 1) if "need_open_comment" in item else None,
            only_fans_can_comment=bool01(item["only_fans_can_comment"], 0) if "only_fans_can_comment" in item else None,
            app_id=item.get("app_id", ""), app_secret=item.get("app_secret", ""),
        ))
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
        return Account(need_open_comment=config.need_open_comment, only_fans_can_comment=config.only_fans_can_comment)
    if alias:
        selected = next((item for item in config.accounts if item.alias == alias), None)
        if selected is None:
            raise WechatError(f"Account alias not found in EXTEND.md: {alias}")
    elif len(config.accounts) == 1:
        selected = config.accounts[0]
    else:
        selected = next((item for item in config.accounts if item.default), None)
    if selected is None:
        available = ", ".join(item.alias for item in config.accounts if item.alias)
        raise WechatError(f"Multiple accounts configured. Pass --account <alias>. Available: {available}")
    return Account(
        name=selected.name, alias=selected.alias, default=selected.default,
        need_open_comment=selected.need_open_comment if selected.need_open_comment is not None else config.need_open_comment,
        only_fans_can_comment=selected.only_fans_can_comment if selected.only_fans_can_comment is not None else config.only_fans_can_comment,
        app_id=selected.app_id, app_secret=selected.app_secret,
    )


def load_credentials(account: Account) -> Tuple[str, str, str, List[str]]:
    home = pathlib.Path.home()
    sources: List[Tuple[str, Dict[str, str], str, str]] = []
    skipped: List[str] = []
    if account.app_id or account.app_secret:
        sources.append(("EXTEND.md account", {"app_id": account.app_id, "app_secret": account.app_secret}, "app_id", "app_secret"))
    scoped_prefix = "WECHAT_" + account.alias.upper().replace("-", "_") + "_" if account.alias else ""
    env_files = [pathlib.Path.cwd() / ".guige-skills" / ".env", home / ".guige-skills" / ".env", pathlib.Path.cwd() / ".baoyu-skills" / ".env", home / ".baoyu-skills" / ".env"]
    if scoped_prefix:
        sources.append(("process.env account", dict(os.environ), scoped_prefix + "APP_ID", scoped_prefix + "APP_SECRET"))
        sources.extend((f"{path} account", parse_env_file(path), scoped_prefix + "APP_ID", scoped_prefix + "APP_SECRET") for path in env_files[:2])
    sources.append(("process.env", dict(os.environ), "WECHAT_APP_ID", "WECHAT_APP_SECRET"))
    sources.extend((str(path), parse_env_file(path), "WECHAT_APP_ID", "WECHAT_APP_SECRET") for path in env_files)
    for name, values, app_key, secret_key in sources:
        app_id, app_secret = values.get(app_key, "").strip(), values.get(secret_key, "").strip()
        if app_id and app_secret:
            return app_id, app_secret, name, skipped
        if app_id or app_secret:
            skipped.append(f"{name} missing {app_key if not app_id else secret_key}")
    hint = f" for account {account.alias}" if account.alias else ""
    raise WechatError(f"Missing WECHAT_APP_ID or WECHAT_APP_SECRET{hint}. Set env vars, .guige-skills/.env, or EXTEND.md account credentials.")


def extract_html_body(content: str) -> str:
    match = re.search(r'<body[^>]*>([\s\S]*?)</body>', content, flags=re.I)
    return match.group(1).strip() if match else content


def load_render_manifest(manifest_path: pathlib.Path, output_html: str = "") -> PublicationInput:
    try:
        data = json.loads(manifest_path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WechatError(f"Invalid render manifest: {manifest_path}: {error}") from error
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        raise WechatError("Unsupported render manifest schemaVersion; expected 1.")

    def required_text(name: str) -> str:
        value = data.get(name)
        if not isinstance(value, str) or not value.strip():
            raise WechatError(f"Render manifest requires a non-empty {name}.")
        return value.strip()

    rendered_html = pathlib.Path(required_text("htmlPath")).expanduser().resolve()
    asset_base = pathlib.Path(required_text("assetBaseDir")).expanduser().resolve()
    if not rendered_html.is_file():
        raise WechatError(f"Rendered HTML not found: {rendered_html}")
    if not asset_base.is_dir():
        raise WechatError(f"Render manifest assetBaseDir is not a directory: {asset_base}")
    images = data.get("contentImages", [])
    if not isinstance(images, list):
        raise WechatError("Render manifest contentImages must be a list.")
    inline_images: List[str] = []
    for image in images:
        if not isinstance(image, dict) or not isinstance(image.get("resolvedPath"), str) or not image["resolvedPath"]:
            raise WechatError("Each render manifest contentImages entry requires resolvedPath.")
        inline_images.append(image["resolvedPath"])
    cover = data.get("cover")
    if cover is not None and not isinstance(cover, dict):
        raise WechatError("Render manifest cover must be an object or null.")
    final_html = pathlib.Path(output_html).expanduser().resolve() if output_html else rendered_html.with_name(rendered_html.stem + ".published.html")
    return PublicationInput(
        title=required_text("title"), summary=str(data.get("summary") or ""), author=str(data.get("author") or ""),
        html_content=extract_html_body(rendered_html.read_text("utf-8")), html_path=str(final_html),
        cover_source=str((cover or {}).get("resolvedPath") or (cover or {}).get("source") or ""),
        inline_images=inline_images, source_path=str(manifest_path.resolve()), base_dir=str(asset_base),
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
    extension = pathlib.Path(filename).suffix.lower()
    return IMAGE_MIME_BY_EXT.get(extension) or mimetypes.guess_type(filename)[0] or "application/octet-stream", extension


def download_url(url: str) -> UploadAsset:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        filename = pathlib.PurePosixPath(urllib.parse.urlparse(response.geturl()).path).name or "image.jpg"
        content_type = (response.headers.get("content-type") or "").split(";", 1)[0].strip()
    detected, extension = infer_content_type(filename, data)
    if not pathlib.Path(filename).suffix and extension:
        filename += extension
    return UploadAsset(data, filename, content_type or detected, url)


def load_asset(path_or_url: str, base_dir: str = "") -> UploadAsset:
    if re.match(r"^https?://", path_or_url):
        return download_url(path_or_url)
    path = pathlib.Path(path_or_url).expanduser()
    path = (path if path.is_absolute() else pathlib.Path(base_dir or os.getcwd()) / path).resolve()
    if not path.is_file():
        raise WechatError(f"Image not found: {path}")
    data = path.read_bytes()
    content_type, extension = infer_content_type(path.name, data)
    return UploadAsset(data, path.name if path.suffix else path.name + extension, content_type, str(path), str(path))


def make_temp_asset(data: bytes, filename: str, content_type: str, source: str) -> UploadAsset:
    path = pathlib.Path(tempfile.mkdtemp(prefix="guige-to-wechat-")) / filename
    path.write_bytes(data)
    return UploadAsset(data, filename, content_type, source, str(path))


def prepare_body_asset(asset: UploadAsset) -> UploadAsset:
    if asset.content_type in BODY_UPLOAD_ALLOWED_MIME and len(asset.data) <= BODY_IMAGE_MAX_SIZE:
        return asset
    source = pathlib.Path(asset.temp_path) if asset.temp_path else pathlib.Path(make_temp_asset(asset.data, asset.filename, asset.content_type, asset.source).temp_path or "")
    for width in [2560, 2048, 1600, 1280, 1024, 800, 640]:
        output = source.with_name(f"{source.stem}-{width}.jpg")
        if shutil.which("sips"):
            command = ["sips", "-s", "format", "jpeg", "-Z", str(width), str(source), "--out", str(output)]
        elif shutil.which("cwebp"):
            command = ["cwebp", "-q", "82", "-resize", str(width), "0", str(source), "-o", str(output)]
        else:
            break
        if subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0 and output.is_file() and output.stat().st_size <= BODY_IMAGE_MAX_SIZE:
            eprint(f"[guige-to-wechat] Converted body image: {asset.filename} -> {output.name}")
            return UploadAsset(output.read_bytes(), output.name, "image/jpeg", asset.source, str(output))
    eprint(f"[guige-to-wechat] Warning: body image may be rejected by WeChat: {asset.filename}")
    return asset


def build_multipart(field: str, asset: UploadAsset) -> Tuple[bytes, str]:
    boundary = "----GuigeWechatBoundary" + dt.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    header = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; filename=\"{asset.filename}\"\r\nContent-Type: {asset.content_type}\r\n\r\n").encode("utf-8")
    return header + asset.data + f"\r\n--{boundary}--\r\n".encode("utf-8"), boundary


def http_json(url: str, method: str = "GET", data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Any:
    request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise WechatError(f"HTTP {error.code}: {error.read().decode('utf-8', errors='replace')[:500]}") from error
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise WechatError(f"Invalid JSON response: {raw[:500]}") from error


def fetch_access_token(app_id: str, app_secret: str) -> str:
    query = urllib.parse.urlencode({"grant_type": "client_credential", "appid": app_id, "secret": app_secret})
    data = http_json(f"{TOKEN_URL}?{query}")
    if data.get("errcode") or not data.get("access_token"):
        raise WechatError(f"Access token error {data.get('errcode')}: {data.get('errmsg')}")
    return data["access_token"]


def upload_image(source: str, access_token: str, base_dir: str, upload_type: str) -> Dict[str, Any]:
    asset = load_asset(source, base_dir)
    if upload_type == "body":
        asset = prepare_body_asset(asset)
        url = f"{UPLOAD_BODY_IMG_URL}?access_token={urllib.parse.quote(access_token)}"
    else:
        url = f"{UPLOAD_MATERIAL_URL}?type=image&access_token={urllib.parse.quote(access_token)}"
    body, boundary = build_multipart("media", asset)
    response = http_json(url, method="POST", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    if response.get("errcode"):
        raise WechatError(f"Upload failed {response.get('errcode')}: {response.get('errmsg')}")
    response["url"] = re.sub(r"^http://", "https://", response.get("url", ""))
    return {"url": response["url"], "media_id": ""} if upload_type == "body" else response


IMG_TAG_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)


def upload_images_in_html(html_content: str, access_token: str, base_dir: str, article_type: str, collect_cover_fallback: bool) -> Tuple[str, str, List[str]]:
    uploaded: Dict[str, Dict[str, Any]] = {}
    first_cover_media_id = ""
    image_media_ids: List[str] = []
    result = html_content
    for match in list(IMG_TAG_RE.finditer(html_content)):
        tag, source = match.group(0), match.group(1)
        if source.startswith("https://mmbiz.qpic.cn"):
            continue
        local = re.search(r'data-local-path=[\"\']([^\"\']+)[\"\']', tag)
        image_source = local.group(1) if local else source
        try:
            body_response = uploaded.get(image_source)
            if not body_response:
                eprint(f"[guige-to-wechat] Uploading body image: {image_source}")
                body_response = upload_image(image_source, access_token, base_dir, "body")
                uploaded[image_source] = body_response
            result = result.replace(tag, re.sub(r'\ssrc=["\'][^"\']+["\']', f' src="{html.escape(body_response["url"], quote=True)}"', tag, count=1))
            if article_type == "newspic" or (collect_cover_fallback and not first_cover_media_id):
                material = uploaded.get(image_source + ":material")
                if not material:
                    material = upload_image(image_source, access_token, base_dir, "material")
                    uploaded[image_source + ":material"] = material
                if article_type == "newspic" and material.get("media_id"):
                    image_media_ids.append(material["media_id"])
                if collect_cover_fallback and not first_cover_media_id:
                    first_cover_media_id = material.get("media_id", "")
        except Exception as error:
            eprint(f"[guige-to-wechat] Failed to upload image {image_source}: {error}")
    return result, first_cover_media_id, image_media_ids


def resolve_cover(rendered: PublicationInput, args: argparse.Namespace) -> str:
    return args.cover or rendered.cover_source


def validate_article_inputs(rendered: PublicationInput, article_type: str, cover: str) -> None:
    has_images = bool(rendered.inline_images) or bool(IMG_TAG_RE.search(rendered.html_content))
    if article_type == "news" and not cover and not has_images:
        raise WechatError("news requires a cover image or at least one inline image for cover fallback.")
    if article_type == "newspic" and not has_images:
        raise WechatError("newspic requires at least one inline image.")


def build_draft_article(title: str, author: str, digest: str, content: str, thumb_media_id: str, article_type: str, image_media_ids: List[str], need_open_comment: int, only_fans_can_comment: int) -> Dict[str, Any]:
    if article_type == "newspic":
        if not image_media_ids:
            raise WechatError("newspic requires at least one inline image.")
        article: Dict[str, Any] = {"article_type": "newspic", "title": title, "content": content, "need_open_comment": need_open_comment, "only_fans_can_comment": only_fans_can_comment, "image_info": {"image_list": [{"image_media_id": item} for item in image_media_ids]}}
    else:
        if not thumb_media_id:
            raise WechatError("news requires a cover image.")
        article = {"article_type": "news", "title": title, "content": content, "thumb_media_id": thumb_media_id, "need_open_comment": need_open_comment, "only_fans_can_comment": only_fans_can_comment}
        if digest:
            article["digest"] = digest
    if author:
        article["author"] = author
    return article


def publish_to_draft(access_token: str, title: str, author: str, digest: str, content: str, thumb_media_id: str, article_type: str, image_media_ids: List[str], need_open_comment: int, only_fans_can_comment: int) -> Dict[str, Any]:
    article = build_draft_article(title, author, digest, content, thumb_media_id, article_type, image_media_ids, need_open_comment, only_fans_can_comment)
    data = http_json(f"{DRAFT_URL}?access_token={urllib.parse.quote(access_token)}", method="POST", data=json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
    if data.get("errcode"):
        raise WechatError(f"Publish failed {data.get('errcode')}: {data.get('errmsg')}")
    return data


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a guige-markdown-to-html render manifest to a WeChat Official Account draft.")
    parser.add_argument("render_manifest", nargs="?", help="Renderer manifest JSON file")
    parser.add_argument("--type", choices=["news", "newspic"], default="news")
    parser.add_argument("--cover", help="Override the manifest cover for this publication")
    parser.add_argument("--account")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-html", default="", help="Write the post-upload HTML to this path")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.render_manifest:
        raise WechatError("Missing render manifest. Run guige-markdown-to-html with --manifest first.")
    config = load_config()
    account = resolve_account(config, args.account or "")
    rendered = load_render_manifest(pathlib.Path(args.render_manifest).expanduser().resolve(), args.output_html)
    cover = resolve_cover(rendered, args)
    validate_article_inputs(rendered, args.type, cover)
    need_open_comment = account.need_open_comment if account.need_open_comment is not None else config.need_open_comment
    only_fans_can_comment = account.only_fans_can_comment if account.only_fans_can_comment is not None else config.only_fans_can_comment
    eprint(f"[guige-to-wechat] Input: {rendered.source_path}")
    eprint(f"[guige-to-wechat] HTML: {rendered.html_path}")
    eprint(f"[guige-to-wechat] Title: {rendered.title}")
    if cover:
        eprint(f"[guige-to-wechat] Cover: {cover}")
    if args.dry_run:
        result = {"success": True, "dryRun": True, "title": rendered.title, "summary": rendered.summary, "author": rendered.author, "articleType": args.type, "htmlPath": rendered.html_path, "input": rendered.source_path, "cover": cover or None, "inlineImages": rendered.inline_images, "comments": {"need_open_comment": need_open_comment, "only_fans_can_comment": only_fans_can_comment}, "config": config.source_path or None, "account": account.alias or None}
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else rendered.html_path)
        return 0
    app_id, app_secret, credential_source, skipped = load_credentials(account)
    for item in skipped:
        eprint(f"[guige-to-wechat] Skipped incomplete credential source: {item}")
    eprint(f"[guige-to-wechat] Credentials: {credential_source}")
    access_token = fetch_access_token(app_id, app_secret)
    processed_html, first_cover_media_id, image_media_ids = upload_images_in_html(rendered.html_content, access_token, rendered.base_dir, args.type, args.type == "news" and not cover)
    thumb_media_id = ""
    if cover:
        thumb_media_id = upload_image(cover, access_token, rendered.base_dir, "material").get("media_id", "")
    elif first_cover_media_id:
        thumb_media_id = first_cover_media_id
    final_html_path = pathlib.Path(rendered.html_path)
    final_html_path.parent.mkdir(parents=True, exist_ok=True)
    final_html_path.write_text("<!doctype html><html><head><meta charset=\"utf-8\"><title>" + html.escape(rendered.title) + "</title></head><body>" + processed_html + "</body></html>\n", "utf-8")
    response = publish_to_draft(access_token, rendered.title, rendered.author, rendered.summary, processed_html, thumb_media_id, args.type, image_media_ids, need_open_comment, only_fans_can_comment)
    result = {"success": True, "media_id": response.get("media_id"), "title": rendered.title, "articleType": args.type, "htmlPath": str(final_html_path)}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
