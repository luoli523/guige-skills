#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import platform
import random
import re
import select
import shutil
import socket
import ssl
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DISCLAIMER_VERSION = "1.0"

DEFAULT_BEARER_TOKEN = (
    "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D"
    "1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

X_COOKIE_NAMES = ("auth_token", "ct0", "gt", "twid")
X_REQUIRED_COOKIES = ("auth_token", "ct0")
X_LOGIN_URL = "https://x.com/home"

FALLBACK_QUERY_ID = "id8pHQbQi7eZ6P9mA1th1Q"
FALLBACK_FEATURE_SWITCHES = [
    "profile_label_improvements_pcf_label_in_post_enabled",
    "responsive_web_profile_redirect_enabled",
    "rweb_tipjar_consumption_enabled",
    "verified_phone_label_enabled",
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
    "responsive_web_graphql_timeline_navigation_enabled",
]
FALLBACK_FIELD_TOGGLES = ["withPayments", "withAuxiliaryUserLabels"]

FALLBACK_TWEET_QUERY_ID = "HJ9lpOL-ZlOk5CkCw0JW6Q"
FALLBACK_TWEET_FEATURE_SWITCHES = [
    "creator_subscriptions_tweet_preview_api_enabled",
    "premium_content_api_read_enabled",
    "communities_web_enable_tweet_community_results_fetch",
    "c9s_tweet_anatomy_moderator_badge_enabled",
    "responsive_web_grok_analyze_button_fetch_trends_enabled",
    "responsive_web_grok_analyze_post_followups_enabled",
    "responsive_web_jetfuel_frame",
    "responsive_web_grok_share_attachment_enabled",
    "responsive_web_grok_annotations_enabled",
    "articles_preview_enabled",
    "responsive_web_edit_tweet_api_enabled",
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled",
    "view_counts_everywhere_api_enabled",
    "longform_notetweets_consumption_enabled",
    "responsive_web_twitter_article_tweet_consumption_enabled",
    "tweet_awards_web_tipping_enabled",
    "responsive_web_grok_show_grok_translated_post",
    "responsive_web_grok_analysis_button_from_backend",
    "post_ctas_fetch_enabled",
    "creator_subscriptions_quote_tweet_preview_enabled",
    "freedom_of_speech_not_reach_fetch_enabled",
    "standardized_nudges_misinfo",
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled",
    "longform_notetweets_rich_text_read_enabled",
    "longform_notetweets_inline_media_enabled",
    "profile_label_improvements_pcf_label_in_post_enabled",
    "responsive_web_profile_redirect_enabled",
    "rweb_tipjar_consumption_enabled",
    "verified_phone_label_enabled",
    "responsive_web_grok_image_annotation_enabled",
    "responsive_web_grok_imagine_annotation_enabled",
    "responsive_web_grok_community_note_auto_translation_is_enabled",
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
    "responsive_web_graphql_timeline_navigation_enabled",
    "responsive_web_enhance_cards_enabled",
]
FALLBACK_TWEET_FIELD_TOGGLES = [
    "withArticleRichContentState",
    "withArticlePlainText",
    "withGrokAnalyze",
    "withDisallowedReplyControls",
    "withPayments",
    "withAuxiliaryUserLabels",
]

FALLBACK_TWEET_DETAIL_QUERY_ID = "_8aYOgEDz35BrBcBal1-_w"
FALLBACK_TWEET_DETAIL_FEATURE_SWITCHES = [
    "rweb_video_screen_enabled",
    "profile_label_improvements_pcf_label_in_post_enabled",
    "rweb_tipjar_consumption_enabled",
    "verified_phone_label_enabled",
    "creator_subscriptions_tweet_preview_api_enabled",
    "responsive_web_graphql_timeline_navigation_enabled",
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
    "premium_content_api_read_enabled",
    "communities_web_enable_tweet_community_results_fetch",
    "c9s_tweet_anatomy_moderator_badge_enabled",
    "responsive_web_grok_analyze_button_fetch_trends_enabled",
    "responsive_web_grok_analyze_post_followups_enabled",
    "responsive_web_jetfuel_frame",
    "responsive_web_grok_share_attachment_enabled",
    "articles_preview_enabled",
    "responsive_web_edit_tweet_api_enabled",
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled",
    "view_counts_everywhere_api_enabled",
    "longform_notetweets_consumption_enabled",
    "responsive_web_twitter_article_tweet_consumption_enabled",
    "tweet_awards_web_tipping_enabled",
    "responsive_web_grok_show_grok_translated_post",
    "responsive_web_grok_analysis_button_from_backend",
    "creator_subscriptions_quote_tweet_preview_enabled",
    "freedom_of_speech_not_reach_fetch_enabled",
    "standardized_nudges_misinfo",
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled",
    "longform_notetweets_rich_text_read_enabled",
    "longform_notetweets_inline_media_enabled",
    "responsive_web_grok_image_annotation_enabled",
    "responsive_web_enhance_cards_enabled",
]
FALLBACK_TWEET_DETAIL_FEATURE_DEFAULTS = {
    "rweb_video_screen_enabled": False,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "rweb_tipjar_consumption_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "responsive_web_jetfuel_frame": False,
    "responsive_web_grok_share_attachment_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "responsive_web_grok_show_grok_translated_post": False,
    "responsive_web_grok_analysis_button_from_backend": True,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}
FALLBACK_TWEET_DETAIL_FIELD_TOGGLES = [
    "withArticleRichContentState",
    "withArticlePlainText",
    "withGrokAnalyze",
    "withDisallowedReplyControls",
]

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "avif", "heic", "heif", "svg"}
VIDEO_EXTENSIONS = {"mp4", "m4v", "mov", "webm", "mkv"}
MIME_EXTENSION_MAP = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/avif": "avif",
    "image/heic": "heic",
    "image/heif": "heif",
    "image/svg+xml": "svg",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "video/x-m4v": "m4v",
}

DOWNLOAD_USER_AGENT = DEFAULT_USER_AGENT
HOME_HTML_CACHE: dict[str, str] = {}


class XToMarkdownError(RuntimeError):
    pass


def log(message: str) -> None:
    print(message, file=sys.stderr)


def data_root() -> pathlib.Path:
    override = os.environ.get("X_DATA_DIR", "").strip()
    if override:
        return pathlib.Path(override).expanduser().resolve()
    system = platform.system().lower()
    if system == "windows":
        root = os.environ.get("APPDATA") or str(pathlib.Path.home() / "AppData" / "Roaming")
    elif system == "darwin":
        root = str(pathlib.Path.home() / "Library" / "Application Support")
    else:
        root = os.environ.get("XDG_DATA_HOME") or str(pathlib.Path.home() / ".local" / "share")
    return pathlib.Path(root) / "guige-skills" / "x-2-md"


def cookie_path() -> pathlib.Path:
    override = os.environ.get("X_COOKIE_PATH", "").strip()
    if override:
        return pathlib.Path(override).expanduser().resolve()
    return data_root() / "cookies.json"


def consent_path() -> pathlib.Path:
    return data_root() / "consent.json"


def chrome_profile_dir() -> pathlib.Path:
    override = os.environ.get("X_CHROME_PROFILE_DIR", "").strip() or os.environ.get(
        "BAOYU_CHROME_PROFILE_DIR", ""
    ).strip()
    if override:
        return pathlib.Path(override).expanduser().resolve()
    return data_root() / "chrome-profile"


def ensure_consent(accept_risk: bool) -> None:
    path = consent_path()
    try:
        if path.is_file():
            raw = json.loads(path.read_text("utf-8"))
            if (
                raw.get("accepted") is True
                and raw.get("disclaimerVersion") == DISCLAIMER_VERSION
                and raw.get("acceptedAt")
            ):
                log(
                    "Warning: using reverse-engineered X API (not official). "
                    f"Accepted on: {raw.get('acceptedAt')}"
                )
                return
    except Exception:
        pass

    disclaimer = """DISCLAIMER

This tool uses reverse-engineered X/Twitter web APIs, NOT the official X API.

Risks:
- It may break without notice if X changes its web API.
- There is no official support or stability guarantee.
- Account restrictions are possible if API usage is detected.
- Use at your own risk.
"""
    log(disclaimer)
    if not accept_risk:
        if not sys.stdin.isatty():
            raise XToMarkdownError(
                f"Consent required. Re-run with --accept-risk or create {path} with "
                f'accepted: true and disclaimerVersion: "{DISCLAIMER_VERSION}".'
            )
        answer = input("Accept terms and continue? (y/N): ").strip().lower()
        if answer not in {"y", "yes"}:
            raise XToMarkdownError("User declined. Exiting.")

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "accepted": True,
        "acceptedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimerVersion": DISCLAIMER_VERSION,
    }
    path.write_text(json.dumps(payload, indent=2), "utf-8")
    log(f"[guige-x-2-md] Consent saved to: {path}")


def normalize_url(input_url: str) -> str:
    return input_url.strip()


def parse_article_id(input_url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(input_url.strip())
    except Exception:
        return None
    match = re.search(r"/(?:i/)?article/(\d+)", parsed.path)
    return match.group(1) if match else None


def parse_tweet_id(input_url: str) -> str | None:
    value = input_url.strip()
    if re.fullmatch(r"\d+", value):
        return value
    try:
        parsed = urllib.parse.urlparse(value)
    except Exception:
        return None
    match = re.search(r"/status(?:es)?/(\d+)", parsed.path)
    return match.group(1) if match else None


def parse_tweet_username(input_url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(input_url.strip())
    except Exception:
        return None
    match = re.match(r"^/([^/]+)/status(?:es)?/\d+", parsed.path)
    return match.group(1) if match else None


def sanitize_slug(value: str, max_len: int = 120) -> str:
    value = value.strip().lstrip("@")
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-_")
    return value[:max_len] or "untitled"


def extract_content_slug(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    if match:
        return sanitize_slug(match.group(1)[:60]).lower()
    in_frontmatter = False
    for line in markdown.splitlines():
        if line == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        trimmed = line.strip()
        if trimmed:
            return sanitize_slug(trimmed[:60]).lower()
    return "untitled"


def read_json_file(path: pathlib.Path) -> Any | None:
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return None


def write_json_file(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), "utf-8")


def build_cookie_map(cookies: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in X_COOKIE_NAMES:
        matches = [c for c in cookies if c.get("name") == name and isinstance(c.get("value"), str)]
        if not matches:
            continue

        def domain_for(cookie: dict[str, Any]) -> str:
            domain = str(cookie.get("domain") or "").strip().lstrip(".")
            if domain:
                return domain
            raw_url = str(cookie.get("url") or "")
            try:
                return urllib.parse.urlparse(raw_url).hostname or ""
            except Exception:
                return ""

        preferred = next(
            (c for c in matches if domain_for(c) == "x.com" and (c.get("path") or "/") == "/"),
            None,
        )
        x_domain = next((c for c in matches if domain_for(c).endswith("x.com")), None)
        twitter_domain = next((c for c in matches if domain_for(c).endswith("twitter.com")), None)
        picked = preferred or x_domain or twitter_domain or matches[0]
        result[name] = str(picked.get("value") or "")
    return {k: v for k, v in result.items() if v}


def has_required_cookies(cookie_map: dict[str, str]) -> bool:
    return all(cookie_map.get(name) for name in X_REQUIRED_COOKIES)


def load_cookies_from_env() -> dict[str, str]:
    cookies: list[dict[str, str]] = []
    env_map = {
        "auth_token": "X_AUTH_TOKEN",
        "ct0": "X_CT0",
        "gt": "X_GUEST_TOKEN",
        "twid": "X_TWID",
    }
    for name, env_name in env_map.items():
        value = os.environ.get(env_name, "").strip()
        if value:
            cookies.append({"name": name, "value": value, "domain": "x.com", "path": "/"})
    cookie_map = build_cookie_map(cookies)
    if cookie_map:
        log(f"[x-cookies] Loaded X cookies from env: {len(cookie_map)} cookie(s).")
    return cookie_map


def load_cookies_from_file() -> dict[str, str]:
    path = cookie_path()
    data = read_json_file(path)
    if not isinstance(data, dict):
        return {}
    raw = data.get("cookies") or data.get("cookieMap") or data
    if not isinstance(raw, dict):
        return {}
    cookie_map = {k: str(v) for k, v in raw.items() if k in X_COOKIE_NAMES and v}
    if cookie_map:
        log(f"[x-cookies] Loaded X cookies from file: {path} ({len(cookie_map)} cookie(s)).")
    return cookie_map


def save_cookies(cookie_map: dict[str, str], source: str) -> None:
    payload = {
        "version": 1,
        "source": source,
        "savedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cookieMap": {k: v for k, v in cookie_map.items() if k in X_COOKIE_NAMES and v},
    }
    write_json_file(cookie_path(), payload)


def find_free_port() -> int:
    override = os.environ.get("X_DEBUG_PORT", "").strip()
    if override:
        return int(override)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def find_chrome_executable() -> str | None:
    override = os.environ.get("X_CHROME_PATH", "").strip()
    if override:
        return override
    system = platform.system().lower()
    candidates: list[str]
    if system == "darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
            "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    elif system == "windows":
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        ]
    else:
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/usr/bin/microsoft-edge",
        ]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    return None


class WebSocket:
    def __init__(self, url: str, timeout: float = 15.0) -> None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"ws", "wss"}:
            raise XToMarkdownError(f"Unsupported websocket URL: {url}")
        self.parsed = parsed
        self.timeout = timeout
        self.sock: socket.socket | ssl.SSLSocket | None = None

    def connect(self) -> None:
        host = self.parsed.hostname or "127.0.0.1"
        port = self.parsed.port or (443 if self.parsed.scheme == "wss" else 80)
        raw_sock = socket.create_connection((host, port), timeout=self.timeout)
        if self.parsed.scheme == "wss":
            raw_sock = ssl.create_default_context().wrap_socket(raw_sock, server_hostname=host)
        raw_sock.settimeout(self.timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        path = self.parsed.path or "/"
        if self.parsed.query:
            path += "?" + self.parsed.query
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        raw_sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = raw_sock.recv(4096)
            if not chunk:
                break
            response += chunk
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise XToMarkdownError(f"Chrome CDP websocket handshake failed: {response[:200]!r}")
        self.sock = raw_sock

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def send_text(self, text: str) -> None:
        if not self.sock:
            raise XToMarkdownError("WebSocket is not connected.")
        payload = text.encode("utf-8")
        first = 0x81
        mask_bit = 0x80
        length = len(payload)
        if length < 126:
            header = struct.pack("!BB", first, mask_bit | length)
        elif length < 65536:
            header = struct.pack("!BBH", first, mask_bit | 126, length)
        else:
            header = struct.pack("!BBQ", first, mask_bit | 127, length)
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def recv_text(self, timeout: float = 15.0) -> str:
        if not self.sock:
            raise XToMarkdownError("WebSocket is not connected.")
        ready, _, _ = select.select([self.sock], [], [], timeout)
        if not ready:
            raise TimeoutError("Timed out waiting for CDP response.")
        first_two = self._recv_exact(2)
        first, second = first_two[0], first_two[1]
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if masked else b""
        payload = self._recv_exact(length) if length else b""
        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        if opcode == 0x8:
            raise XToMarkdownError("CDP websocket closed.")
        if opcode == 0x9:
            return self.recv_text(timeout)
        return payload.decode("utf-8", errors="replace")

    def _recv_exact(self, n: int) -> bytes:
        if not self.sock:
            raise XToMarkdownError("WebSocket is not connected.")
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise XToMarkdownError("Unexpected websocket EOF.")
            data += chunk
        return data


class CdpConnection:
    def __init__(self, ws_url: str) -> None:
        self.ws = WebSocket(ws_url)
        self.next_id = 1

    def __enter__(self) -> "CdpConnection":
        self.ws.connect()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.ws.close()

    def send(self, method: str, params: dict[str, Any] | None = None, session_id: str | None = None) -> Any:
        msg_id = self.next_id
        self.next_id += 1
        payload: dict[str, Any] = {"id": msg_id, "method": method}
        if params is not None:
            payload["params"] = params
        if session_id:
            payload["sessionId"] = session_id
        self.ws.send_text(json.dumps(payload, separators=(",", ":")))
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                raw = self.ws.recv_text(timeout=max(0.1, deadline - time.time()))
            except TimeoutError:
                continue
            data = json.loads(raw)
            if data.get("id") != msg_id:
                continue
            if "error" in data:
                raise XToMarkdownError(f"CDP error for {method}: {data['error']}")
            return data.get("result")
        raise TimeoutError(f"Timed out waiting for CDP method {method}.")


def fetch_text(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise XToMarkdownError(f"Request failed ({error.code}) for {url}: {body[:400]}") from error


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> Any:
    text = fetch_text(url, headers=headers, timeout=timeout)
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise XToMarkdownError(f"Failed to parse JSON response from {url}: {error}") from error


def wait_for_chrome(port: int, timeout_s: float = 30.0) -> str:
    deadline = time.time() + timeout_s
    url = f"http://127.0.0.1:{port}/json/version"
    last_error = ""
    while time.time() < deadline:
        try:
            data = fetch_json(url, timeout=2)
            ws_url = data.get("webSocketDebuggerUrl")
            if isinstance(ws_url, str) and ws_url:
                return ws_url
        except Exception as error:
            last_error = str(error)
        time.sleep(0.5)
    raise XToMarkdownError(f"Timed out waiting for Chrome debug port {port}. Last error: {last_error}")


def refresh_cookies_via_chrome() -> dict[str, str]:
    chrome_path = find_chrome_executable()
    if not chrome_path:
        raise XToMarkdownError("Chrome or Edge executable not found. Set X_CHROME_PATH.")
    profile = chrome_profile_dir()
    profile.mkdir(parents=True, exist_ok=True)
    port = find_free_port()
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile}",
        "--disable-popup-blocking",
        X_LOGIN_URL,
    ]
    log(f"[x-cookies] Opening browser on debug port {port}. Complete X login if needed.")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = wait_for_chrome(port)
        with CdpConnection(ws_url) as cdp:
            target = cdp.send("Target.createTarget", {"url": X_LOGIN_URL})
            target_id = target.get("targetId")
            attached = cdp.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
            session_id = attached.get("sessionId")
            cdp.send("Network.enable", {}, session_id=session_id)
            deadline = time.time() + 300
            last_keys: list[str] = []
            while time.time() < deadline:
                result = cdp.send(
                    "Network.getCookies",
                    {"urls": ["https://x.com/", "https://twitter.com/"]},
                    session_id=session_id,
                )
                cookie_map = build_cookie_map(result.get("cookies") or [])
                last_keys = sorted(cookie_map.keys())
                if has_required_cookies(cookie_map):
                    save_cookies(cookie_map, "cdp")
                    log(f"[x-cookies] Cookies saved to {cookie_path()}")
                    try:
                        cdp.send("Target.closeTarget", {"targetId": target_id})
                    except Exception:
                        pass
                    return cookie_map
                time.sleep(1)
            raise XToMarkdownError(f"Timed out waiting for X cookies. Last keys: {', '.join(last_keys)}")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def load_cookies(auto_chrome: bool = True) -> dict[str, str]:
    file_map = load_cookies_from_file()
    env_map = load_cookies_from_env()
    combined = {**file_map, **env_map}
    if has_required_cookies(combined):
        return combined
    if not auto_chrome:
        return combined
    cdp_map = refresh_cookies_via_chrome()
    return {**file_map, **cdp_map, **env_map}


def build_cookie_header(cookie_map: dict[str, str]) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookie_map.items() if v)


def fetch_home_html(user_agent: str) -> str:
    cached = HOME_HTML_CACHE.get(user_agent)
    if cached is not None:
        return cached
    html = fetch_text("https://x.com", headers={"user-agent": user_agent})
    HOME_HTML_CACHE[user_agent] = html
    return html


def parse_string_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip().strip('"') for item in raw.split(",") if item.strip()]


def resolve_feature_value(html: str, key: str) -> bool | None:
    escaped_key = re.escape(key)
    patterns = [
        rf'"{escaped_key}"\s*:\s*\{{"value"\s*:\s*(true|false)',
        rf'\\"{escaped_key}\\"\s*:\s*\\{{\\"value\\"\s*:\s*(true|false)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1) == "true"
    return None


def build_feature_map(
    html: str, keys: list[str], defaults: dict[str, bool] | None = None
) -> dict[str, bool]:
    features: dict[str, bool] = {}
    for key in keys:
        value = resolve_feature_value(html, key)
        if value is not None:
            features[key] = value
        elif defaults and key in defaults:
            features[key] = defaults[key]
        else:
            features[key] = True
    features.setdefault("responsive_web_graphql_exclude_directive_enabled", True)
    return features


def build_field_toggle_map(keys: list[str]) -> dict[str, bool]:
    return {key: True for key in keys}


def build_tweet_field_toggle_map(keys: list[str]) -> dict[str, bool]:
    return {key: False if key in {"withGrokAnalyze", "withDisallowedReplyControls"} else True for key in keys}


def build_tweet_detail_field_toggle_map(keys: list[str]) -> dict[str, bool]:
    toggles = build_field_toggle_map(keys)
    for key in ("withArticlePlainText", "withGrokAnalyze", "withDisallowedReplyControls"):
        if key in toggles:
            toggles[key] = False
    return toggles


def build_request_headers(cookie_map: dict[str, str], user_agent: str, bearer_token: str) -> dict[str, str]:
    headers = {
        "authorization": bearer_token,
        "user-agent": user_agent,
        "accept": "application/json",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
        "accept-language": "en",
    }
    if cookie_map.get("auth_token"):
        headers["x-twitter-auth-type"] = "OAuth2Session"
    if cookie_map:
        headers["cookie"] = build_cookie_header(cookie_map)
    if cookie_map.get("ct0"):
        headers["x-csrf-token"] = cookie_map["ct0"]
    client_transaction_id = os.environ.get("X_CLIENT_TRANSACTION_ID", "").strip()
    if client_transaction_id:
        headers["x-client-transaction-id"] = client_transaction_id
    return headers


@dataclass
class QueryInfo:
    query_id: str
    feature_switches: list[str]
    field_toggles: list[str]
    html: str


def resolve_article_query_info(user_agent: str) -> QueryInfo:
    html = fetch_home_html(user_agent)
    bundle_match = re.search(r'"bundle\\.TwitterArticles":"([a-z0-9]+)"', html)
    if not bundle_match:
        return QueryInfo(FALLBACK_QUERY_ID, FALLBACK_FEATURE_SWITCHES, FALLBACK_FIELD_TOGGLES, html)
    chunk = fetch_text(
        f"https://abs.twimg.com/responsive-web/client-web/bundle.TwitterArticles.{bundle_match.group(1)}a.js",
        headers={"user-agent": user_agent},
    )
    query_match = re.search(r'queryId:"([^"]+)",operationName:"ArticleEntityResultByRestId"', chunk)
    feature_match = re.search(
        r'operationName:"ArticleEntityResultByRestId"[\s\S]*?featureSwitches:\[(.*?)\]', chunk
    )
    field_match = re.search(
        r'operationName:"ArticleEntityResultByRestId"[\s\S]*?fieldToggles:\[(.*?)\]', chunk
    )
    features = parse_string_list(feature_match.group(1) if feature_match else None) or FALLBACK_FEATURE_SWITCHES
    fields = parse_string_list(field_match.group(1) if field_match else None) or FALLBACK_FIELD_TOGGLES
    return QueryInfo(query_match.group(1) if query_match else FALLBACK_QUERY_ID, features, fields, html)


def resolve_main_chunk_hash(html: str) -> str | None:
    match = re.search(r"main\.([a-z0-9]+)\.js", html)
    return match.group(1) if match else None


def resolve_api_chunk_hash(html: str) -> str | None:
    match = re.search(r'api:"([a-zA-Z0-9_-]+)"', html)
    return match.group(1) if match else None


def resolve_tweet_query_info(user_agent: str) -> QueryInfo:
    html = fetch_home_html(user_agent)
    main_hash = resolve_main_chunk_hash(html)
    if not main_hash:
        return QueryInfo(FALLBACK_TWEET_QUERY_ID, FALLBACK_TWEET_FEATURE_SWITCHES, FALLBACK_TWEET_FIELD_TOGGLES, html)
    chunk = fetch_text(
        f"https://abs.twimg.com/responsive-web/client-web/main.{main_hash}.js",
        headers={"user-agent": user_agent},
    )
    query_match = re.search(r'queryId:"([^"]+)",operationName:"TweetResultByRestId"', chunk)
    feature_match = re.search(r'operationName:"TweetResultByRestId"[\s\S]*?featureSwitches:\[(.*?)\]', chunk)
    field_match = re.search(r'operationName:"TweetResultByRestId"[\s\S]*?fieldToggles:\[(.*?)\]', chunk)
    features = parse_string_list(feature_match.group(1) if feature_match else None) or FALLBACK_TWEET_FEATURE_SWITCHES
    fields = parse_string_list(field_match.group(1) if field_match else None) or FALLBACK_TWEET_FIELD_TOGGLES
    return QueryInfo(query_match.group(1) if query_match else FALLBACK_TWEET_QUERY_ID, features, fields, html)


def resolve_tweet_detail_query_info(user_agent: str) -> QueryInfo:
    html = fetch_home_html(user_agent)
    api_hash = resolve_api_chunk_hash(html)
    if not api_hash:
        return QueryInfo(
            FALLBACK_TWEET_DETAIL_QUERY_ID,
            FALLBACK_TWEET_DETAIL_FEATURE_SWITCHES,
            FALLBACK_TWEET_DETAIL_FIELD_TOGGLES,
            html,
        )
    chunk = fetch_text(
        f"https://abs.twimg.com/responsive-web/client-web/api.{api_hash}a.js",
        headers={"user-agent": user_agent},
    )
    query_match = re.search(r'queryId:"([^"]+)",operationName:"TweetDetail"', chunk)
    feature_match = re.search(r'operationName:"TweetDetail"[\s\S]*?featureSwitches:\[(.*?)\]', chunk)
    field_match = re.search(r'operationName:"TweetDetail"[\s\S]*?fieldToggles:\[(.*?)\]', chunk)
    features = (
        parse_string_list(feature_match.group(1) if feature_match else None)
        or FALLBACK_TWEET_DETAIL_FEATURE_SWITCHES
    )
    fields = (
        parse_string_list(field_match.group(1) if field_match else None)
        or FALLBACK_TWEET_DETAIL_FIELD_TOGGLES
    )
    return QueryInfo(query_match.group(1) if query_match else FALLBACK_TWEET_DETAIL_QUERY_ID, features, fields, html)


def graphql_get(operation_url: str, params: dict[str, Any], headers: dict[str, str]) -> Any:
    query = urllib.parse.urlencode(
        {key: json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list)) else value for key, value in params.items()}
    )
    return fetch_json(f"{operation_url}?{query}", headers=headers)


def unwrap_tweet_result(result: Any) -> Any:
    if isinstance(result, dict) and result.get("__typename") == "TweetWithVisibilityResults" and result.get("tweet"):
        return result.get("tweet")
    return result


def extract_tweet_from_payload(payload: Any) -> Any:
    root = payload.get("data", payload) if isinstance(payload, dict) else payload
    result = get_in(root, ["tweetResult", "result"]) or get_in(root, ["tweet_result", "result"]) or (
        root.get("tweet_result") if isinstance(root, dict) else None
    )
    return unwrap_tweet_result(result)


def extract_article_from_tweet_payload(payload: Any) -> Any:
    tweet = extract_tweet_from_payload(payload)
    legacy = tweet.get("legacy", {}) if isinstance(tweet, dict) else {}
    article = legacy.get("article") or (tweet.get("article") if isinstance(tweet, dict) else None)
    return (
        get_in(article, ["article_results", "result"])
        or get_in(legacy, ["article_results", "result"])
        or get_in(tweet, ["article_results", "result"])
    )


def extract_article_from_entity_payload(payload: Any) -> Any:
    root = payload.get("data", payload) if isinstance(payload, dict) else payload
    return (
        get_in(root, ["article_result_by_rest_id", "result"])
        or root.get("article_result_by_rest_id")
        or get_in(root, ["article_entity_result", "result"])
    )


def fetch_tweet_result(tweet_id: str, cookie_map: dict[str, str], user_agent: str, bearer_token: str) -> Any:
    info = resolve_tweet_query_info(user_agent)
    features = build_feature_map(info.html, info.feature_switches)
    field_toggles = build_tweet_field_toggle_map(info.field_toggles)
    params: dict[str, Any] = {
        "variables": {"tweetId": tweet_id, "withCommunity": False, "includePromotedContent": False, "withVoice": True}
    }
    if features:
        params["features"] = features
    if field_toggles:
        params["fieldToggles"] = field_toggles
    url = f"https://x.com/i/api/graphql/{info.query_id}/TweetResultByRestId"
    return graphql_get(url, params, build_request_headers(cookie_map, user_agent, bearer_token))


def fetch_tweet_detail(tweet_id: str, cookie_map: dict[str, str], cursor: str | None = None) -> Any:
    user_agent = os.environ.get("X_USER_AGENT", "").strip() or DEFAULT_USER_AGENT
    bearer_token = os.environ.get("X_BEARER_TOKEN", "").strip() or DEFAULT_BEARER_TOKEN
    info = resolve_tweet_detail_query_info(user_agent)
    features = build_feature_map(info.html, info.feature_switches, FALLBACK_TWEET_DETAIL_FEATURE_DEFAULTS)
    field_toggles = build_tweet_detail_field_toggle_map(info.field_toggles)
    variables = {
        "focalTweetId": tweet_id,
        "cursor": cursor,
        "referrer": "tweet" if cursor else None,
        "with_rux_injections": False,
        "includePromotedContent": True,
        "withCommunity": True,
        "withQuickPromoteEligibilityTweetFields": True,
        "withBirdwatchNotes": True,
        "withVoice": True,
        "withV2Timeline": True,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withSuperFollowsTweetFields": False,
        "withSuperFollowsUserFields": False,
    }
    variables = {k: v for k, v in variables.items() if v is not None}
    params: dict[str, Any] = {"variables": variables}
    if features:
        params["features"] = features
    if field_toggles:
        params["fieldToggles"] = field_toggles
    url = f"https://x.com/i/api/graphql/{info.query_id}/TweetDetail"
    return graphql_get(url, params, build_request_headers(cookie_map, user_agent, bearer_token))


def fetch_article_entity_by_id(article_id: str, cookie_map: dict[str, str], user_agent: str, bearer_token: str) -> Any:
    info = resolve_article_query_info(user_agent)
    features = build_feature_map(info.html, info.feature_switches)
    field_toggles = build_field_toggle_map(info.field_toggles)
    params: dict[str, Any] = {"variables": {"articleEntityId": article_id}}
    if features:
        params["features"] = features
    if field_toggles:
        params["fieldToggles"] = field_toggles
    url = f"https://x.com/i/api/graphql/{info.query_id}/ArticleEntityResultByRestId"
    return graphql_get(url, params, build_request_headers(cookie_map, user_agent, bearer_token))


def fetch_x_article(article_id: str, cookie_map: dict[str, str]) -> Any:
    user_agent = os.environ.get("X_USER_AGENT", "").strip() or DEFAULT_USER_AGENT
    bearer_token = os.environ.get("X_BEARER_TOKEN", "").strip() or DEFAULT_BEARER_TOKEN
    tweet_payload = fetch_tweet_result(article_id, cookie_map, user_agent, bearer_token)
    article_from_tweet = extract_article_from_tweet_payload(tweet_payload)
    if is_non_empty_dict(article_from_tweet):
        return article_from_tweet
    article_payload = fetch_article_entity_by_id(article_id, cookie_map, user_agent, bearer_token)
    article_from_entity = extract_article_from_entity_payload(article_payload)
    return article_from_entity if article_from_entity is not None else article_payload


def fetch_x_tweet(tweet_id: str, cookie_map: dict[str, str]) -> Any:
    user_agent = os.environ.get("X_USER_AGENT", "").strip() or DEFAULT_USER_AGENT
    bearer_token = os.environ.get("X_BEARER_TOKEN", "").strip() or DEFAULT_BEARER_TOKEN
    payload = fetch_tweet_result(tweet_id, cookie_map, user_agent, bearer_token)
    tweet = extract_tweet_from_payload(payload)
    return tweet if tweet is not None else payload


def get_in(value: Any, path: list[str]) -> Any:
    cur = value
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def is_non_empty_dict(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def extract_tweet_entry(item_content: Any) -> dict[str, Any] | None:
    result = get_in(item_content, ["tweet_results", "result"])
    if not result:
        return None
    resolved = unwrap_tweet_result((result.get("tweet") or result) if isinstance(result, dict) else result)
    if not resolved:
        return None
    user = get_in(resolved, ["core", "user_results", "result", "legacy"])
    return {"tweet": resolved, "user": user}


def parse_instruction(instruction: Any) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    more_cursor = None
    top_cursor = None
    bottom_cursor = None

    def parse_items(items: Any) -> None:
        nonlocal more_cursor
        if not isinstance(items, list):
            return
        for item in items:
            item_content = get_in(item, ["item", "itemContent"]) or item.get("itemContent")
            if not item_content:
                continue
            if (
                item_content.get("cursorType") in {"ShowMore", "ShowMoreThreads"}
                and item_content.get("itemType") == "TimelineTimelineCursor"
            ):
                more_cursor = item_content.get("value")
                continue
            entry = extract_tweet_entry(item_content)
            if entry:
                entries.append(entry)

    if not isinstance(instruction, dict):
        return {"entries": entries}
    parse_items(instruction.get("moduleItems"))
    for entity in instruction.get("entries") or []:
        content = entity.get("content") or {}
        if get_in(content, ["clientEventInfo", "component"]) == "you_might_also_like":
            continue
        item_content = content.get("itemContent")
        items = content.get("items")
        cursor_type = content.get("cursorType")
        entry_type = content.get("entryType")
        value = content.get("value")
        if cursor_type == "Bottom" and entry_type == "TimelineTimelineCursor":
            bottom_cursor = value
        if item_content and item_content.get("cursorType") == "Bottom" and item_content.get("itemType") == "TimelineTimelineCursor":
            bottom_cursor = bottom_cursor or item_content.get("value")
        if cursor_type == "Top" and entry_type == "TimelineTimelineCursor":
            top_cursor = top_cursor or value
        if item_content:
            entry = extract_tweet_entry(item_content)
            if entry:
                entries.append(entry)
            if (
                item_content.get("cursorType") in {"ShowMore", "ShowMoreThreads"}
                and item_content.get("itemType") == "TimelineTimelineCursor"
            ):
                more_cursor = more_cursor or item_content.get("value")
            if item_content.get("cursorType") == "Top" and item_content.get("itemType") == "TimelineTimelineCursor":
                top_cursor = top_cursor or item_content.get("value")
        if items:
            parse_items(items)
    return {
        "entries": entries,
        "moreCursor": more_cursor,
        "topCursor": top_cursor,
        "bottomCursor": bottom_cursor,
    }


def parse_tweets_and_token(response: Any) -> dict[str, Any]:
    instructions = (
        get_in(response, ["data", "threaded_conversation_with_injections_v2", "instructions"])
        or get_in(response, ["data", "threaded_conversation_with_injections", "instructions"])
        or []
    )
    for instruction in instructions:
        if instruction.get("type") in {"TimelineAddEntries", "TimelineAddToModule"}:
            return parse_instruction(instruction)
    return {"entries": []}


def tweet_created_timestamp(tweet: Any) -> float:
    raw = get_in(tweet, ["legacy", "created_at"])
    if not isinstance(raw, str) or not raw:
        return 0
    try:
        from email.utils import parsedate_to_datetime

        return parsedate_to_datetime(raw).timestamp()
    except Exception:
        return 0


def fetch_tweet_thread(tweet_id: str, cookie_map: dict[str, str]) -> dict[str, Any]:
    response = fetch_tweet_detail(tweet_id, cookie_map)
    parsed = parse_tweets_and_token(response)
    entries = list(parsed.get("entries") or [])
    more_cursor = parsed.get("moreCursor")
    top_cursor = parsed.get("topCursor")
    bottom_cursor = parsed.get("bottomCursor")
    if not entries:
        error_message = get_in(response, ["errors", 0, "message"])
        raise XToMarkdownError(error_message or "No tweets found in thread.")
    all_entries = list(entries)
    root = next((e for e in all_entries if get_in(e, ["tweet", "legacy", "id_str"]) == tweet_id), None)
    if not root:
        raise XToMarkdownError("Can not fetch the root tweet.")
    root_entry = get_in(root, ["tweet", "legacy"])

    def is_same_thread(entry: dict[str, Any]) -> bool:
        tweet = get_in(entry, ["tweet", "legacy"])
        if not isinstance(tweet, dict) or not isinstance(root_entry, dict):
            return False
        return (
            tweet.get("user_id_str") == root_entry.get("user_id_str")
            and tweet.get("conversation_id_str") == root_entry.get("conversation_id_str")
            and (
                tweet.get("id_str") == root_entry.get("id_str")
                or tweet.get("in_reply_to_user_id_str") == root_entry.get("user_id_str")
                or tweet.get("in_reply_to_status_id_str") == root_entry.get("conversation_id_str")
                or not tweet.get("in_reply_to_user_id_str")
            )
        )

    def in_thread(items: list[dict[str, Any]]) -> bool:
        return any(is_same_thread(item) for item in items)

    has_thread = in_thread(entries)
    max_request_count = 1000
    top_has_thread = True
    while top_cursor and top_has_thread and max_request_count > 0:
        new_response = fetch_tweet_detail(tweet_id, cookie_map, str(top_cursor))
        new_parsed = parse_tweets_and_token(new_response)
        new_entries = list(new_parsed.get("entries") or [])
        top_has_thread = in_thread(new_entries)
        top_cursor = new_parsed.get("topCursor")
        all_entries = new_entries + all_entries
        max_request_count -= 1

    def check_more_tweets(focal_id: str) -> None:
        nonlocal more_cursor, bottom_cursor, has_thread, all_entries, max_request_count
        while more_cursor and has_thread and max_request_count > 0:
            new_response = fetch_tweet_detail(focal_id, cookie_map, str(more_cursor))
            new_parsed = parse_tweets_and_token(new_response)
            new_entries = list(new_parsed.get("entries") or [])
            more_cursor = new_parsed.get("moreCursor")
            bottom_cursor = bottom_cursor or new_parsed.get("bottomCursor")
            has_thread = in_thread(new_entries)
            all_entries.extend(new_entries)
            max_request_count -= 1
        if bottom_cursor:
            new_response = fetch_tweet_detail(focal_id, cookie_map, str(bottom_cursor))
            new_parsed = parse_tweets_and_token(new_response)
            all_entries.extend(list(new_parsed.get("entries") or []))
            bottom_cursor = None

    check_more_tweets(tweet_id)
    all_thread_entries = [e for e in all_entries if get_in(e, ["tweet", "legacy", "id_str"]) == tweet_id or is_same_thread(e)]
    last_entity = all_thread_entries[-1] if all_thread_entries else None
    last_id = get_in(last_entity, ["tweet", "legacy", "id_str"])
    if last_id:
        last_response = fetch_tweet_detail(str(last_id), cookie_map)
        last_parsed = parse_tweets_and_token(last_response)
        last_entries = list(last_parsed.get("entries") or [])
        has_thread = in_thread(last_entries)
        all_entries.extend(last_entries)
        more_cursor = last_parsed.get("moreCursor")
        bottom_cursor = last_parsed.get("bottomCursor")
        max_request_count -= 1
        check_more_tweets(str(last_id))

    distinct: list[dict[str, Any]] = []
    entries_map: dict[str, dict[str, Any]] = {}
    for entry in all_entries:
        entry_id = get_in(entry, ["tweet", "legacy", "id_str"]) or get_in(entry, ["tweet", "rest_id"])
        if entry_id and entry_id not in entries_map:
            entries_map[str(entry_id)] = entry
            distinct.append(entry)
    all_entries = distinct

    while isinstance(root_entry, dict) and root_entry.get("in_reply_to_status_id_str"):
        parent = get_in(entries_map.get(str(root_entry.get("in_reply_to_status_id_str"))), ["tweet", "legacy"])
        if (
            isinstance(parent, dict)
            and parent.get("user_id_str") == root_entry.get("user_id_str")
            and parent.get("conversation_id_str") == root_entry.get("conversation_id_str")
            and parent.get("id_str") != root_entry.get("id_str")
        ):
            root_entry = parent
        else:
            break

    all_entries.sort(key=lambda e: tweet_created_timestamp(e.get("tweet")))
    root_id = root_entry.get("id_str") if isinstance(root_entry, dict) else tweet_id
    root_index = next((i for i, e in enumerate(all_entries) if get_in(e, ["tweet", "legacy", "id_str"]) == root_id), -1)
    if root_index > 0:
        all_entries = all_entries[root_index:]
    thread_entries = [e for e in all_entries if get_in(e, ["tweet", "legacy", "id_str"]) == tweet_id or is_same_thread(e)]
    if not thread_entries:
        raise XToMarkdownError("No matching thread entries found.")
    tweets = [e["tweet"] for e in thread_entries]
    user = thread_entries[0].get("user") or get_in(thread_entries[0], ["tweet", "core", "user_results", "result", "legacy"])
    return {
        "requestedId": tweet_id,
        "rootId": root_id or tweet_id,
        "tweets": tweets,
        "totalTweets": len(tweets),
        "user": user,
    }


def parse_tweet_text(tweet: Any) -> str:
    return (
        get_in(tweet, ["note_tweet", "note_tweet_results", "result", "text"])
        or get_in(tweet, ["legacy", "full_text"])
        or get_in(tweet, ["legacy", "text"])
        or ""
    ).strip()


def normalize_alt(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.strip())


def escape_markdown_alt(text: str) -> str:
    return text.replace("[", r"\[").replace("]", r"\]")


def parse_photos(tweet: Any) -> list[dict[str, str]]:
    media = get_in(tweet, ["legacy", "extended_entities", "media"]) or []
    photos = []
    for item in media:
        if item.get("type") != "photo":
            continue
        src = item.get("media_url_https") or item.get("media_url")
        if src:
            photos.append({"src": src, "alt": normalize_alt(item.get("ext_alt_text"))})
    return photos


def parse_videos(tweet: Any) -> list[dict[str, str]]:
    media = get_in(tweet, ["legacy", "extended_entities", "media"]) or []
    videos = []
    for item in media:
        if item.get("type") not in {"animated_gif", "video"}:
            continue
        variants = get_in(item, ["video_info", "variants"]) or []
        sources = [
            {
                "content_type": variant.get("content_type"),
                "url": variant.get("url"),
                "bitrate": variant.get("bitrate") or 0,
            }
            for variant in variants
            if variant.get("url")
        ]
        video_sources = [s for s in sources if "video" in str(s.get("content_type") or "")]
        sorted_sources = sorted(video_sources or sources, key=lambda s: s.get("bitrate") or 0, reverse=True)
        if not sorted_sources:
            continue
        best = sorted_sources[0]
        videos.append(
            {
                "url": best["url"],
                "poster": item.get("media_url_https") or item.get("media_url") or "",
                "alt": normalize_alt(item.get("ext_alt_text")),
                "type": item.get("type") or "video",
            }
        )
    return videos


def resolve_tweet_id(tweet: Any) -> str | None:
    return get_in(tweet, ["legacy", "id_str"]) or tweet.get("rest_id") if isinstance(tweet, dict) else None


def build_tweet_url(username: str | None, tweet_id: str | None) -> str | None:
    if not tweet_id:
        return None
    if username:
        return f"https://x.com/{username}/status/{tweet_id}"
    return f"https://x.com/i/web/status/{tweet_id}"


def format_quoted_tweet_markdown(quoted: Any) -> list[str]:
    if not quoted:
        return []
    user = get_in(quoted, ["core", "user_results", "result", "legacy"]) or {}
    username = user.get("screen_name")
    name = user.get("name")
    if username and name:
        author = f"{name} (@{username})"
    elif username:
        author = f"@{username}"
    else:
        author = name or "Unknown"
    tweet_id = resolve_tweet_id(quoted)
    url = build_tweet_url(username, tweet_id) or (f"https://x.com/i/web/status/{tweet_id}" if tweet_id else "unavailable")
    text = parse_tweet_text(quoted)
    lines = [f"Author: {author}", f"URL: {url}", ""]
    lines.extend(text.splitlines() if text else ["(no content)"])
    return [("> " + line).rstrip() for line in lines]


def format_thread_tweets_markdown(
    tweets: list[Any],
    username: str | None = None,
    heading_level: int = 2,
    start_index: int = 1,
    include_tweet_urls: bool = True,
) -> str:
    output: list[str] = []
    prefix = "#" * min(max(heading_level, 1), 6)
    for offset, tweet in enumerate(tweets):
        if output:
            output.append("")
        tweet_id = resolve_tweet_id(tweet)
        tweet_url = build_tweet_url(username, tweet_id) if include_tweet_urls else None
        output.append(f"{prefix} {start_index + offset}")
        if tweet_url:
            output.append(tweet_url)
        output.append("")
        body: list[str] = []
        text = parse_tweet_text(tweet)
        if text:
            body.extend(text.splitlines())
        quoted = unwrap_tweet_result(get_in(tweet, ["quoted_status_result", "result"]))
        quoted_lines = format_quoted_tweet_markdown(quoted)
        if quoted_lines:
            if body:
                body.append("")
            body.extend(quoted_lines)
        photo_lines = [
            f"![{escape_markdown_alt(photo.get('alt') or '')}]({photo['src']})" for photo in parse_photos(tweet)
        ]
        if photo_lines:
            if body:
                body.append("")
            body.extend(photo_lines)
        video_lines: list[str] = []
        for video in parse_videos(tweet):
            if video.get("poster"):
                alt = escape_markdown_alt(video.get("alt") or "video")
                video_lines.append(f"![{alt}]({video['poster']})")
            video_lines.append(f"[{video.get('type') or 'video'}]({video['url']})")
        if video_lines:
            if body:
                body.append("")
            body.extend(video_lines)
        output.extend(body or ["_No text or media._"])
    return "\n".join(output).rstrip()


def format_frontmatter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if value is None or value == "":
            continue
        if isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {json.dumps(str(value), ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def coerce_article_entity(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    if (
        isinstance(value.get("title"), str)
        or isinstance(value.get("plain_text"), str)
        or isinstance(value.get("preview_text"), str)
        or value.get("content_state")
    ):
        return value
    return None


def resolve_video_url(info: dict[str, Any] | None) -> str | None:
    if not info:
        return None
    variants = info.get("variants") or []
    mp4 = sorted(
        [v for v in variants if "video" in str(v.get("content_type") or "")],
        key=lambda v: v.get("bit_rate") or v.get("bitrate") or 0,
        reverse=True,
    )
    if mp4:
        return mp4[0].get("url")
    for variant in variants:
        if isinstance(variant.get("url"), str):
            return variant.get("url")
    return None


def resolve_media_asset(info: dict[str, Any] | None) -> dict[str, str] | None:
    if not info:
        return None
    poster_url = get_in(info, ["preview_image", "original_img_url"]) or info.get("original_img_url")
    video_url = resolve_video_url(info)
    if video_url:
        return {"kind": "video", "url": video_url, "posterUrl": poster_url or ""}
    image_url = info.get("original_img_url") or get_in(info, ["preview_image", "original_img_url"])
    if image_url:
        return {"kind": "image", "url": image_url}
    return None


def resolve_fallback_media_asset(raw_url: str | None) -> dict[str, str] | None:
    if not raw_url:
        return None
    if re.search(r"^https://video\.twimg\.com/", raw_url, re.I) or re.search(r"\.(mp4|m4v|mov|webm)(?:$|[?#])", raw_url, re.I):
        return {"kind": "video", "url": raw_url}
    return {"kind": "image", "url": raw_url}


def resolve_cover_url(info: dict[str, Any] | None) -> str | None:
    if not info:
        return None
    return info.get("original_img_url") or get_in(info, ["preview_image", "original_img_url"])


def build_media_identity(asset: dict[str, str]) -> str:
    if asset.get("kind") == "video":
        return f"video:{asset.get('url')}:{asset.get('posterUrl', '')}"
    return f"image:{asset.get('url')}"


def render_media_lines(asset: dict[str, str], alt_text: str, used_urls: set[str]) -> list[str]:
    if asset.get("kind") == "video":
        lines = []
        poster = asset.get("posterUrl")
        if poster and poster not in used_urls:
            used_urls.add(poster)
            lines.append(f"![{alt_text or 'video'}]({poster})")
        url = asset.get("url")
        if url and url not in used_urls:
            used_urls.add(url)
            lines.append(f"[video]({url})")
        return lines
    url = asset.get("url")
    if not url or url in used_urls:
        return []
    used_urls.add(url)
    return [f"![{alt_text}]({url})"]


def build_media_by_id(article: dict[str, Any]) -> dict[str, dict[str, str]]:
    media_by_id = {}
    for entity in article.get("media_entities") or []:
        media_id = entity.get("media_id")
        asset = resolve_media_asset(entity.get("media_info"))
        if media_id and asset:
            media_by_id[str(media_id)] = asset
    return media_by_id


def collect_media_assets(article: dict[str, Any]) -> list[dict[str, str]]:
    assets = []
    seen = set()
    for entity in article.get("media_entities") or []:
        asset = resolve_media_asset(entity.get("media_info"))
        if not asset:
            continue
        ident = build_media_identity(asset)
        if ident in seen:
            continue
        seen.add(ident)
        assets.append(asset)
    return assets


def build_entity_lookup(entity_map: dict[str, Any] | None) -> tuple[dict[int, Any], dict[int, Any]]:
    by_index: dict[int, Any] = {}
    by_logical_key: dict[int, Any] = {}
    if not isinstance(entity_map, dict):
        return by_index, by_logical_key
    for idx, entry in entity_map.items():
        try:
            by_index[int(idx)] = entry
        except Exception:
            pass
        try:
            logical = int(str(entry.get("key")))
            by_logical_key.setdefault(logical, entry)
        except Exception:
            pass
    return by_index, by_logical_key


def resolve_entity_entry(entity_key: int | None, lookup: tuple[dict[int, Any], dict[int, Any]]) -> Any:
    if entity_key is None:
        return None
    by_index, by_logical_key = lookup
    return by_logical_key.get(entity_key) or by_index.get(entity_key)


def normalize_caption(caption: Any) -> str:
    return re.sub(r"\s+", " ", caption.strip()) if isinstance(caption, str) and caption.strip() else ""


def resolve_entity_media_lines(
    entity_key: int | None,
    lookup: tuple[dict[int, Any], dict[int, Any]],
    media_by_id: dict[str, dict[str, str]],
    used_urls: set[str],
) -> list[str]:
    entry = resolve_entity_entry(entity_key, lookup)
    value = entry.get("value") if isinstance(entry, dict) else None
    if not isinstance(value, dict) or value.get("type") not in {"MEDIA", "IMAGE"}:
        return []
    caption = normalize_caption(get_in(value, ["data", "caption"]))
    alt_text = escape_markdown_alt(caption) if caption else ""
    lines: list[str] = []
    for item in get_in(value, ["data", "mediaItems"]) or []:
        media_id = item.get("mediaId") or item.get("media_id")
        asset = media_by_id.get(str(media_id)) if media_id else None
        if asset:
            lines.extend(render_media_lines(asset, alt_text, used_urls))
    fallback_url = get_in(value, ["data", "url"])
    fallback_asset = resolve_fallback_media_asset(fallback_url)
    if fallback_asset:
        lines.extend(render_media_lines(fallback_asset, alt_text, used_urls))
    return lines


def summarize_tweet_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return normalized if len(normalized) <= 280 else normalized[:277] + "..."


def resolve_entity_tweet_lines(
    entity_key: int | None,
    lookup: tuple[dict[int, Any], dict[int, Any]],
    referenced_tweets: dict[str, dict[str, str]] | None,
) -> list[str]:
    entry = resolve_entity_entry(entity_key, lookup)
    value = entry.get("value") if isinstance(entry, dict) else None
    if not isinstance(value, dict) or value.get("type") != "TWEET":
        return []
    tweet_id = get_in(value, ["data", "tweetId"])
    if not tweet_id:
        return []
    referenced = (referenced_tweets or {}).get(str(tweet_id), {})
    url = referenced.get("url") or build_tweet_url(referenced.get("authorUsername"), str(tweet_id)) or f"https://x.com/i/web/status/{tweet_id}"
    if referenced.get("authorName") and referenced.get("authorUsername"):
        author = f"{referenced['authorName']} (@{referenced['authorUsername']})"
    elif referenced.get("authorUsername"):
        author = f"@{referenced['authorUsername']}"
    else:
        author = referenced.get("authorName", "")
    lines = [f"> Referenced tweet{': ' + author if author else ''}"]
    summary = summarize_tweet_text(referenced.get("text"))
    if summary:
        lines.append(f"> {summary}")
    lines.append(f"> {url}")
    return lines


def resolve_entity_markdown_lines(entity_key: int | None, lookup: tuple[dict[int, Any], dict[int, Any]]) -> list[str]:
    entry = resolve_entity_entry(entity_key, lookup)
    value = entry.get("value") if isinstance(entry, dict) else None
    if not isinstance(value, dict) or value.get("type") != "MARKDOWN":
        return []
    markdown = get_in(value, ["data", "markdown"])
    if not isinstance(markdown, str) or not markdown.strip():
        return []
    return markdown.replace("\r\n", "\n").rstrip().splitlines()


def build_media_link_map(entity_map: dict[str, Any] | None) -> dict[int, str]:
    result: dict[int, str] = {}
    if not isinstance(entity_map, dict):
        return result
    media_entries: list[tuple[int, int]] = []
    link_entries: list[tuple[int, str]] = []
    for idx, entry in entity_map.items():
        value = entry.get("value") if isinstance(entry, dict) else None
        if not isinstance(value, dict):
            continue
        try:
            key = int(str(entry.get("key")))
        except Exception:
            continue
        if value.get("type") in {"MEDIA", "IMAGE"}:
            try:
                media_entries.append((int(idx), key))
            except Exception:
                pass
        elif value.get("type") == "LINK" and isinstance(get_in(value, ["data", "url"]), str):
            link_entries.append((key, get_in(value, ["data", "url"])))
    media_entries.sort(key=lambda item: item[1])
    link_entries.sort(key=lambda item: item[0])
    pool = list(link_entries)
    for idx, key in media_entries:
        if not pool:
            break
        link_idx = next((i for i, item in enumerate(pool) if item[0] > key), 0)
        _, url = pool.pop(link_idx)
        result[idx] = url
        result[key] = url
    return result


def render_inline_links(
    text: str,
    entity_ranges: list[dict[str, Any]],
    lookup: tuple[dict[int, Any], dict[int, Any]],
    media_link_map: dict[int, str],
) -> str:
    valid = [
        r
        for r in entity_ranges
        if isinstance(r.get("key"), int) and isinstance(r.get("offset"), int) and isinstance(r.get("length"), int) and r["length"] > 0
    ]
    result = text
    for item in sorted(valid, key=lambda r: r["offset"], reverse=True):
        entry = resolve_entity_entry(item["key"], lookup)
        value = entry.get("value") if isinstance(entry, dict) else None
        if not isinstance(value, dict):
            continue
        url = None
        if value.get("type") == "LINK":
            url = get_in(value, ["data", "url"])
        elif value.get("type") in {"MEDIA", "IMAGE"}:
            url = media_link_map.get(item["key"])
        if not url:
            continue
        start = item["offset"]
        end = start + item["length"]
        link_text = result[start:end]
        result = result[:start] + f"[{link_text}]({url})" + result[end:]
    return result


def render_content_blocks(
    blocks: list[dict[str, Any]],
    entity_map: dict[str, Any] | None,
    media_by_id: dict[str, dict[str, str]],
    used_urls: set[str],
    referenced_tweets: dict[str, dict[str, str]] | None = None,
) -> list[str]:
    lookup = build_entity_lookup(entity_map)
    media_link_map = build_media_link_map(entity_map)
    lines: list[str] = []
    previous_kind: str | None = None
    list_kind: str | None = None
    ordered_index = 0
    in_code_block = False

    def push_block(block_lines: list[str], kind: str) -> None:
        nonlocal previous_kind
        if not block_lines:
            return
        if lines and previous_kind and not (previous_kind == kind and kind in {"list", "quote", "media"}):
            lines.append("")
        lines.extend(block_lines)
        previous_kind = kind

    def collect_lines(block: dict[str, Any], resolver: Any) -> list[str]:
        output: list[str] = []
        for r in block.get("entityRanges") or []:
            if isinstance(r.get("key"), int):
                output.extend(resolver(r["key"]))
        return output

    def trailing_media(block: dict[str, Any]) -> None:
        media = collect_lines(block, lambda key: resolve_entity_media_lines(key, lookup, media_by_id, used_urls))
        if media:
            push_block(media, "media")

    for block in blocks:
        block_type = block.get("type") if isinstance(block.get("type"), str) else "unstyled"
        raw_text = block.get("text") if isinstance(block.get("text"), str) else ""
        ranges = block.get("entityRanges") or []
        text = raw_text if block_type in {"atomic", "code-block"} else render_inline_links(raw_text, ranges, lookup, media_link_map)

        if block_type == "code-block":
            if not in_code_block:
                if lines:
                    lines.append("")
                lines.append("```")
                in_code_block = True
            lines.append(text)
            previous_kind = "code"
            list_kind = None
            ordered_index = 0
            continue

        if block_type == "atomic":
            if in_code_block:
                lines.append("```")
                in_code_block = False
                previous_kind = "code"
            list_kind = None
            ordered_index = 0
            tweet_lines = collect_lines(block, lambda key: resolve_entity_tweet_lines(key, lookup, referenced_tweets))
            if tweet_lines:
                push_block(tweet_lines, "quote")
            markdown_lines = collect_lines(block, lambda key: resolve_entity_markdown_lines(key, lookup))
            if markdown_lines:
                push_block(markdown_lines, "text")
            media_lines = collect_lines(block, lambda key: resolve_entity_media_lines(key, lookup, media_by_id, used_urls))
            if media_lines:
                push_block(media_lines, "media")
            link_lines = []
            for r in ranges:
                entry = resolve_entity_entry(r.get("key"), lookup)
                value = entry.get("value") if isinstance(entry, dict) else None
                if isinstance(value, dict) and value.get("type") == "LINK" and get_in(value, ["data", "url"]):
                    link_lines.append(get_in(value, ["data", "url"]))
            if link_lines:
                push_block(list(dict.fromkeys(link_lines)), "text")
            continue

        if in_code_block:
            lines.append("```")
            in_code_block = False
            previous_kind = "code"

        if block_type == "unordered-list-item":
            list_kind = "unordered"
            ordered_index = 0
            push_block([f"- {text}"], "list")
            trailing_media(block)
            continue
        if block_type == "ordered-list-item":
            if list_kind != "ordered":
                ordered_index = 0
            list_kind = "ordered"
            ordered_index += 1
            push_block([f"{ordered_index}. {text}"], "list")
            trailing_media(block)
            continue

        list_kind = None
        ordered_index = 0
        heading_map = {
            "header-one": "#",
            "header-two": "##",
            "header-three": "###",
            "header-four": "####",
            "header-five": "#####",
            "header-six": "######",
        }
        if block_type in heading_map:
            push_block([f"{heading_map[block_type]} {text}"], "heading")
            trailing_media(block)
        elif block_type == "blockquote":
            quote_lines = text.splitlines() if text else [""]
            push_block([f"> {line}" for line in quote_lines], "quote")
            trailing_media(block)
        else:
            if re.fullmatch(r"XIMGPH_\d+", text.strip()):
                trailing_media(block)
            else:
                push_block([text], "text")
                trailing_media(block)
    if in_code_block:
        lines.append("```")
    return lines


def extract_referenced_tweet_ids(article: Any) -> list[str]:
    candidate = coerce_article_entity(article)
    entity_map = get_in(candidate, ["content_state", "entityMap"]) if candidate else None
    if not isinstance(entity_map, dict):
        return []
    ids: list[str] = []
    seen = set()
    for entry in entity_map.values():
        value = entry.get("value") if isinstance(entry, dict) else None
        if isinstance(value, dict) and value.get("type") == "TWEET":
            tweet_id = get_in(value, ["data", "tweetId"])
            if tweet_id and tweet_id not in seen:
                seen.add(tweet_id)
                ids.append(str(tweet_id))
    return ids


def extract_referenced_tweet_info(tweet: Any, fallback_id: str) -> dict[str, str]:
    user_core = get_in(tweet, ["core", "user_results", "result", "core"]) or {}
    user_legacy = get_in(tweet, ["core", "user_results", "result", "legacy"]) or {}
    author_name = user_core.get("name") or user_legacy.get("name") or ""
    author_username = user_core.get("screen_name") or user_legacy.get("screen_name") or ""
    text = (
        get_in(tweet, ["note_tweet", "note_tweet_results", "result", "text"])
        or get_in(tweet, ["legacy", "full_text"])
        or get_in(tweet, ["legacy", "text"])
        or ""
    )
    tweet_id = tweet.get("rest_id") if isinstance(tweet, dict) and tweet.get("rest_id") else fallback_id
    url = build_tweet_url(author_username, str(tweet_id)) or f"https://x.com/i/web/status/{tweet_id}"
    return {
        "id": str(tweet_id),
        "url": url,
        "authorName": str(author_name),
        "authorUsername": str(author_username),
        "text": str(text),
    }


def resolve_referenced_tweets(article: Any, cookie_map: dict[str, str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for tweet_id in extract_referenced_tweet_ids(article):
        try:
            tweet = fetch_x_tweet(tweet_id, cookie_map)
            result[tweet_id] = extract_referenced_tweet_info(tweet, tweet_id)
        except Exception as error:
            log(f"[guige-x-2-md] Failed to fetch referenced tweet {tweet_id}: {error}")
            result[tweet_id] = {"id": tweet_id, "url": f"https://x.com/i/web/status/{tweet_id}"}
    return result


def format_article_markdown(article: Any, referenced_tweets: dict[str, dict[str, str]] | None = None) -> tuple[str, str | None]:
    candidate = coerce_article_entity(article)
    if not candidate:
        return "```json\n" + json.dumps(article, indent=2, ensure_ascii=False) + "\n```", None
    lines: list[str] = []
    used_urls: set[str] = set()
    media_by_id = build_media_by_id(candidate)
    title = candidate.get("title").strip() if isinstance(candidate.get("title"), str) else ""
    if title:
        lines.append(f"# {title}")
    cover_url = resolve_cover_url(get_in(candidate, ["cover_media", "media_info"]))
    if cover_url:
        used_urls.add(cover_url)
    blocks = get_in(candidate, ["content_state", "blocks"])
    entity_map = get_in(candidate, ["content_state", "entityMap"])
    if isinstance(blocks, list) and blocks:
        rendered = render_content_blocks(blocks, entity_map, media_by_id, used_urls, referenced_tweets)
        if rendered:
            if lines:
                lines.append("")
            lines.extend(rendered)
    elif isinstance(candidate.get("plain_text"), str):
        if lines:
            lines.append("")
        lines.append(candidate["plain_text"].strip())
    elif isinstance(candidate.get("preview_text"), str):
        if lines:
            lines.append("")
        lines.append(candidate["preview_text"].strip())
    trailing: list[str] = []
    for asset in collect_media_assets(candidate):
        trailing.extend(render_media_lines(asset, "", used_urls))
    if trailing:
        lines.extend(["", "## Media", ""])
        lines.extend(trailing)
    return "\n".join(lines).rstrip(), cover_url


def extract_article_entity_from_tweet(tweet: Any) -> Any:
    return (
        get_in(tweet, ["article", "article_results", "result"])
        or get_in(tweet, ["article", "result"])
        or get_in(tweet, ["legacy", "article", "article_results", "result"])
        or get_in(tweet, ["legacy", "article", "result"])
        or get_in(tweet, ["article_results", "result"])
    )


def has_article_content(article: dict[str, Any]) -> bool:
    blocks = get_in(article, ["content_state", "blocks"])
    return bool(blocks) or bool(str(article.get("plain_text") or "").strip()) or bool(str(article.get("preview_text") or "").strip())


def extract_article_id_from_urls(urls: Any) -> str | None:
    if not isinstance(urls, list):
        return None
    for item in urls:
        candidate = item.get("expanded_url") or item.get("url")
        if not candidate and item.get("display_url"):
            candidate = "https://" + item["display_url"]
        article_id = parse_article_id(str(candidate or ""))
        if article_id:
            return article_id
    return None


def extract_article_id_from_tweet(tweet: Any) -> str | None:
    embedded = extract_article_entity_from_tweet(tweet)
    if isinstance(embedded, dict) and embedded.get("rest_id"):
        return str(embedded["rest_id"])
    note_urls = get_in(tweet, ["note_tweet", "note_tweet_results", "result", "entity_set", "urls"])
    legacy_urls = get_in(tweet, ["legacy", "entities", "urls"])
    return extract_article_id_from_urls(note_urls) or extract_article_id_from_urls(legacy_urls)


def resolve_article_entity_from_tweet(tweet: Any, cookie_map: dict[str, str]) -> Any:
    embedded = extract_article_entity_from_tweet(tweet)
    embedded_article = coerce_article_entity(embedded)
    if embedded_article and has_article_content(embedded_article):
        return embedded
    article_id = extract_article_id_from_tweet(tweet)
    if not article_id:
        return embedded
    return fetch_x_article(article_id, cookie_map) or embedded


def is_only_url(text: str) -> bool:
    text = text.strip()
    return not text or bool(re.fullmatch(r"https?://\S+", text))


def tweet_to_markdown(input_url: str, cookie_map: dict[str, str]) -> str:
    normalized = normalize_url(input_url)
    tweet_id = parse_tweet_id(normalized)
    if not tweet_id:
        raise XToMarkdownError("Invalid tweet URL. Example: https://x.com/<user>/status/<tweet_id>")
    log(f"[tweet-to-markdown] Fetching thread for {tweet_id}...")
    thread = fetch_tweet_thread(tweet_id, cookie_map)
    tweets = thread.get("tweets") or []
    if not tweets:
        raise XToMarkdownError("No tweets found in thread.")
    first_tweet = tweets[0]
    user = thread.get("user") or get_in(first_tweet, ["core", "user_results", "result", "legacy"]) or {}
    username = user.get("screen_name")
    name = user.get("name")
    if username and name:
        author = f"{name} (@{username})"
    elif username:
        author = f"@{username}"
    else:
        author = name or None
    author_url = f"https://x.com/{username}" if username else None
    requested_url = normalized or build_tweet_url(username, tweet_id) or input_url.strip()
    root_url = build_tweet_url(username, thread.get("rootId") or tweet_id) or requested_url

    article_entity = resolve_article_entity_from_tweet(first_tweet, cookie_map)
    cover_image = None
    remaining_tweets = tweets
    parts: list[str] = []
    if article_entity:
        referenced = resolve_referenced_tweets(article_entity, cookie_map)
        article_markdown, cover_image = format_article_markdown(article_entity, referenced)
        if article_markdown.strip():
            parts.append(article_markdown.rstrip())
            if is_only_url(parse_tweet_text(first_tweet)):
                remaining_tweets = tweets[1:]

    meta = format_frontmatter(
        {
            "url": root_url,
            "requestedUrl": requested_url,
            "author": author,
            "authorName": name,
            "authorUsername": username,
            "authorUrl": author_url,
            "tweetCount": thread.get("totalTweets") or len(tweets),
            "coverImage": cover_image,
        }
    )
    parts.insert(0, meta)
    if remaining_tweets:
        has_article = len(parts) > 1
        if has_article:
            parts.append("## Thread")
        tweet_markdown = format_thread_tweets_markdown(
            remaining_tweets,
            username=username,
            heading_level=3 if has_article else 2,
            start_index=1,
            include_tweet_urls=True,
        )
        if tweet_markdown:
            parts.append(tweet_markdown)
    return "\n\n".join(parts).rstrip()


def article_to_markdown(input_url: str, article_id: str, cookie_map: dict[str, str]) -> str:
    log(f"[guige-x-2-md] Fetching article {article_id}...")
    article = fetch_x_article(article_id, cookie_map)
    referenced = resolve_referenced_tweets(article, cookie_map)
    body, cover_url = format_article_markdown(article, referenced)
    title = article.get("title", "").strip() if isinstance(article, dict) and isinstance(article.get("title"), str) else ""
    meta = format_frontmatter(
        {
            "url": f"https://x.com/i/article/{article_id}",
            "requestedUrl": input_url,
            "title": title,
            "coverImage": cover_url,
        }
    )
    return "\n\n".join([meta, body.rstrip()]).rstrip()


def resolve_output_path(
    normalized_url: str, kind: str, output: str | None, content_slug: str
) -> tuple[pathlib.Path, pathlib.Path, str]:
    article_id = parse_article_id(normalized_url) if kind == "article" else None
    tweet_id = parse_tweet_id(normalized_url) if kind == "tweet" else None
    username = parse_tweet_username(normalized_url) if kind == "tweet" else None
    id_part = article_id or tweet_id or str(int(time.time()))
    slug = sanitize_slug(username) if username else id_part
    default_file = f"{content_slug}.md"
    if output:
        raw = pathlib.Path(output).expanduser()
        wants_dir = output.endswith("/") or output.endswith("\\")
        resolved = raw.resolve()
        if wants_dir or (resolved.exists() and resolved.is_dir()):
            out_dir = resolved / slug / id_part
            out_dir.mkdir(parents=True, exist_ok=True)
            return out_dir, out_dir / default_file, slug
        out_dir = resolved.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir, resolved, slug
    out_dir = pathlib.Path.cwd() / "x-to-markdown" / slug / id_part
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir, out_dir / default_file, slug


def extract_frontmatter_urls(markdown: str) -> list[str]:
    match = re.match(r"---\n(.*?)\n---", markdown, flags=re.S)
    if not match:
        return []
    urls = []
    for line in match.group(1).splitlines():
        m = re.match(r"^(url|requestedUrl):\s*[\"']([^\"']+)[\"']\s*$", line)
        if m:
            urls.append(m.group(2))
    return urls


def frontmatter_matches_target(markdown: str, normalized_url: str, kind: str) -> bool:
    target_id = parse_article_id(normalized_url) if kind == "article" else parse_tweet_id(normalized_url)
    if not target_id:
        return False
    for url in extract_frontmatter_urls(markdown):
        candidate_id = parse_article_id(url) if kind == "article" else parse_tweet_id(url)
        if candidate_id == target_id:
            return True
    return False


def resolve_existing_markdown_path(normalized_url: str, kind: str, output: str | None) -> pathlib.Path | None:
    article_id = parse_article_id(normalized_url) if kind == "article" else None
    tweet_id = parse_tweet_id(normalized_url) if kind == "tweet" else None
    username = parse_tweet_username(normalized_url) if kind == "tweet" else None
    id_part = article_id or tweet_id
    if not id_part:
        return None
    slug = sanitize_slug(username) if username else id_part
    candidate_dirs: set[pathlib.Path] = set()
    candidate_files: set[pathlib.Path] = set()
    if output:
        resolved = pathlib.Path(output).expanduser().resolve()
        looks_dir = output.endswith("/") or output.endswith("\\")
        if resolved.exists():
            if resolved.is_file():
                candidate_files.add(resolved)
            elif resolved.is_dir():
                candidate_dirs.add(resolved / slug / id_part)
                candidate_dirs.add(resolved)
        elif looks_dir:
            candidate_dirs.add(resolved / slug / id_part)
    else:
        candidate_dirs.add(pathlib.Path.cwd() / "x-to-markdown" / slug / id_part)
    for file_path in candidate_files:
        if file_path.suffix.lower() != ".md":
            continue
        try:
            if frontmatter_matches_target(file_path.read_text("utf-8"), normalized_url, kind):
                return file_path
        except Exception:
            pass
    for directory in candidate_dirs:
        if not directory.is_dir():
            continue
        for file_path in sorted(directory.glob("*.md")):
            try:
                if frontmatter_matches_target(file_path.read_text("utf-8"), normalized_url, kind):
                    return file_path
            except Exception:
                pass
    return None


MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]\n]*\])\((<)?(https?://[^)\s>]+)(>)?\)")
FRONTMATTER_COVER_RE = re.compile(r'^(coverImage:\s*")(https?://[^"]+)(")', re.MULTILINE)


def normalize_extension(value: str | None) -> str | None:
    if not value:
        return None
    value = value.lstrip(".").strip().lower()
    if not value:
        return None
    return "jpg" if value in {"jpeg", "jpg"} else value


def resolve_extension_from_url(raw_url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(raw_url)
        ext = normalize_extension(pathlib.PurePosixPath(parsed.path).suffix)
        if ext:
            return ext
        query = urllib.parse.parse_qs(parsed.query)
        fmt = query.get("format", [None])[0]
        return normalize_extension(fmt)
    except Exception:
        return None


def resolve_kind_from_hostname(raw_url: str) -> str | None:
    try:
        host = urllib.parse.urlparse(raw_url).hostname or ""
    except Exception:
        return None
    if "video.twimg.com" in host:
        return "video"
    if "pbs.twimg.com" in host:
        return "image"
    return None


def to_high_res_url(raw_url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(raw_url)
        if parsed.hostname != "pbs.twimg.com":
            return raw_url
        path = parsed.path
        ext = pathlib.PurePosixPath(path).suffix.lstrip(".").lower()
        if not ext or ext not in IMAGE_EXTENSIONS:
            return raw_url
        new_path = re.sub(rf"\.{re.escape(ext)}$", "", path)
        query = dict(urllib.parse.parse_qsl(parsed.query))
        query["format"] = "jpg" if ext == "jpeg" else ext
        query["name"] = "4096x4096"
        return urllib.parse.urlunparse(parsed._replace(path=new_path, query=urllib.parse.urlencode(query)))
    except Exception:
        return raw_url


def is_plausible_media_url(raw_url: str) -> bool:
    ext = resolve_extension_from_url(raw_url)
    return bool(ext and (ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS)) or resolve_kind_from_hostname(raw_url) is not None


def collect_markdown_link_candidates(markdown: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[str] = set()
    fm_match = re.match(r"---\n(.*?)\n---", markdown, flags=re.S)
    if fm_match:
        cover_match = FRONTMATTER_COVER_RE.search(fm_match.group(1))
        if cover_match and cover_match.group(2) not in seen:
            seen.add(cover_match.group(2))
            candidates.append((cover_match.group(2), "image"))
    for match in MARKDOWN_LINK_RE.finditer(markdown):
        label = match.group(1)
        raw_url = match.group(3)
        if raw_url in seen:
            continue
        is_image = label.startswith("![")
        if not is_image and not is_plausible_media_url(raw_url):
            continue
        seen.add(raw_url)
        candidates.append((raw_url, "image" if is_image else "unknown"))
    return candidates


def sanitize_file_segment(value: str) -> str:
    value = urllib.parse.unquote(value)
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-_")
    return value[:48]


def resolve_file_stem(raw_url: str, extension: str) -> str:
    try:
        base = pathlib.PurePosixPath(urllib.parse.urlparse(raw_url).path).name
        if not base:
            return ""
        stem = re.sub(rf"\.{re.escape(extension)}$", "", urllib.parse.unquote(base), flags=re.I)
        return sanitize_file_segment(stem)
    except Exception:
        return ""


def build_file_name(kind: str, index: int, source_url: str, extension: str) -> str:
    stem = resolve_file_stem(source_url, extension)
    prefix = "img" if kind == "image" else "video"
    return f"{prefix}-{index:03d}{'-' + stem if stem else ''}.{extension}"


def rewrite_markdown_media_links(markdown: str, replacements: dict[str, str]) -> str:
    if not replacements:
        return markdown

    def replace_link(match: re.Match[str]) -> str:
        local = replacements.get(match.group(3))
        return f"{match.group(1)}({local})" if local else match.group(0)

    result = MARKDOWN_LINK_RE.sub(replace_link, markdown)

    def replace_cover(match: re.Match[str]) -> str:
        local = replacements.get(match.group(2))
        return f"{match.group(1)}{local}{match.group(3)}" if local else match.group(0)

    return FRONTMATTER_COVER_RE.sub(replace_cover, result)


def localize_markdown_media(markdown: str, markdown_path: pathlib.Path) -> dict[str, Any]:
    candidates = collect_markdown_link_candidates(markdown)
    if not candidates:
        return {
            "markdown": markdown,
            "downloadedImages": 0,
            "downloadedVideos": 0,
            "imageDir": None,
            "videoDir": None,
        }
    markdown_dir = markdown_path.parent
    replacements: dict[str, str] = {}
    downloaded_images = 0
    downloaded_videos = 0
    for raw_url, hint in candidates:
        try:
            download_url = to_high_res_url(raw_url)
            request = urllib.request.Request(download_url, headers={"user-agent": DOWNLOAD_USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
                source_url = response.geturl() or raw_url
                content_type = (response.headers.get("content-type") or "").split(";")[0].strip().lower()
            ext = resolve_extension_from_url(source_url) or resolve_extension_from_url(raw_url)
            if content_type.startswith("image/"):
                kind = "image"
            elif content_type.startswith("video/"):
                kind = "video"
            elif ext in IMAGE_EXTENSIONS:
                kind = "image"
            elif ext in VIDEO_EXTENSIONS:
                kind = "video"
            else:
                kind = resolve_kind_from_hostname(source_url) or ("image" if hint == "image" else None)
            if not kind:
                continue
            out_ext = normalize_extension(MIME_EXTENSION_MAP.get(content_type)) or normalize_extension(ext) or ("mp4" if kind == "video" else "jpg")
            if kind == "image":
                downloaded_images += 1
                index = downloaded_images
                directory = markdown_dir / "imgs"
            else:
                downloaded_videos += 1
                index = downloaded_videos
                directory = markdown_dir / "videos"
            directory.mkdir(parents=True, exist_ok=True)
            file_name = build_file_name(kind, index, source_url, out_ext)
            (directory / file_name).write_bytes(data)
            replacements[raw_url] = f"{directory.name}/{file_name}"
        except Exception as error:
            log(f"[guige-x-2-md] Failed to download media {raw_url}: {error}")
    return {
        "markdown": rewrite_markdown_media_links(markdown, replacements),
        "downloadedImages": downloaded_images,
        "downloadedVideos": downloaded_videos,
        "imageDir": str(markdown_dir / "imgs") if downloaded_images else None,
        "videoDir": str(markdown_dir / "videos") if downloaded_videos else None,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert X/Twitter tweets, threads, and articles to Markdown.")
    parser.add_argument("positional_url", nargs="?", help="X/Twitter status or article URL")
    parser.add_argument("--url", dest="url", help="X/Twitter status or article URL")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    parser.add_argument("--download-media", action="store_true", help="Download images/videos locally")
    parser.add_argument("--login", action="store_true", help="Refresh cookies through Chrome/Edge and exit")
    parser.add_argument("--accept-risk", action="store_true", help="Accept reverse-engineered API risk non-interactively")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    ensure_consent(args.accept_risk)
    if args.login:
        cookie_map = refresh_cookies_via_chrome()
        if not has_required_cookies(cookie_map):
            raise XToMarkdownError("Missing auth cookies after browser login.")
        log("[guige-x-2-md] Cookies refreshed.")
        return 0

    input_url = args.url or args.positional_url
    if not input_url:
        raise XToMarkdownError("Missing URL. Use --help for usage.")
    normalized_url = normalize_url(input_url)
    article_id = parse_article_id(normalized_url)
    tweet_id = parse_tweet_id(normalized_url)
    if not article_id and not tweet_id:
        raise XToMarkdownError("Invalid X URL. Expected status URL or https://x.com/i/article/<id>.")
    kind = "article" if article_id else "tweet"

    log("[guige-x-2-md] Loading cookies...")
    cookie_map = load_cookies(auto_chrome=True)
    if not has_required_cookies(cookie_map):
        raise XToMarkdownError("Missing auth cookies. Provide X_AUTH_TOKEN and X_CT0 or run --login.")

    if args.download_media:
        existing = resolve_existing_markdown_path(normalized_url, kind, args.output)
        if existing:
            log(f"[guige-x-2-md] Reusing existing markdown: {existing}")
            existing_markdown = existing.read_text("utf-8")
            localized = localize_markdown_media(existing_markdown, existing)
            if localized["markdown"] != existing_markdown or localized["downloadedImages"] or localized["downloadedVideos"]:
                existing.write_text(localized["markdown"], "utf-8")
                emit_result(args, normalized_url, kind, existing.parent, existing, True, localized)
                return 0
            log("[guige-x-2-md] Existing markdown already localized; rebuilding content.")

    markdown = article_to_markdown(normalized_url, article_id, cookie_map) if article_id else tweet_to_markdown(normalized_url, cookie_map)
    content_slug = extract_content_slug(markdown)
    output_dir, markdown_path, slug = resolve_output_path(normalized_url, kind, args.output, content_slug)
    localized: dict[str, Any] | None = None
    if args.download_media:
        localized = localize_markdown_media(markdown, markdown_path)
        markdown = localized["markdown"]
        log(
            f"[guige-x-2-md] Media localized: images={localized['downloadedImages']}, "
            f"videos={localized['downloadedVideos']}"
        )
    markdown_path.write_text(markdown, "utf-8")
    log(f"[guige-x-2-md] Saved: {markdown_path}")
    emit_result(args, normalized_url, kind, output_dir, markdown_path, bool(args.download_media), localized, slug=slug)
    return 0


def emit_result(
    args: argparse.Namespace,
    normalized_url: str,
    kind: str,
    output_dir: pathlib.Path,
    markdown_path: pathlib.Path,
    download_media: bool,
    localized: dict[str, Any] | None,
    slug: str | None = None,
) -> None:
    if args.json:
        result = {
            "url": f"https://x.com/i/article/{parse_article_id(normalized_url)}" if kind == "article" else normalized_url,
            "requestedUrl": normalized_url,
            "type": kind,
            "slug": slug,
            "outputDir": str(output_dir),
            "markdownPath": str(markdown_path),
            "downloadMedia": download_media,
            "downloadedImages": localized.get("downloadedImages", 0) if localized else 0,
            "downloadedVideos": localized.get("downloadedVideos", 0) if localized else 0,
            "imageDir": localized.get("imageDir") if localized else None,
            "videoDir": localized.get("videoDir") if localized else None,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(str(markdown_path))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
