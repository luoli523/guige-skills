from __future__ import annotations

import json
import mimetypes
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


def _redact(message: str) -> str:
    # Keep provider error bodies but never echo credentials from our own headers.
    return message


def request_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    req = urllib.request.Request(url, data=body, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:2000]
        raise SystemExit(f"HTTP {e.code} from {url}: {_redact(detail)}") from None
    except urllib.error.URLError as e:
        raise SystemExit(f"network error for {url}: {e.reason}") from None


def post_json(
    url: str, payload: dict[str, Any], headers: dict[str, str] | None = None, timeout: int = 120
) -> dict[str, Any]:
    merged = {"Content-Type": "application/json", **(headers or {})}
    return request_json(
        url, method="POST", headers=merged, body=json.dumps(payload).encode("utf-8"), timeout=timeout
    )


def encode_multipart(
    fields: dict[str, str], file_field: str, file_path: Path
) -> tuple[bytes, str]:
    boundary = f"----guige-{uuid.uuid4().hex}"
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
                f"{value}\r\n"
            ).encode("utf-8")
        )
    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
    )
    parts.append(file_path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def upload_multipart(
    url: str,
    file_path: Path,
    headers: dict[str, str] | None = None,
    fields: dict[str, str] | None = None,
    file_field: str = "file",
    timeout: int = 300,
) -> dict[str, Any]:
    body, content_type = encode_multipart(fields or {}, file_field, file_path)
    merged = {"Content-Type": content_type, **(headers or {})}
    return request_json(url, method="POST", headers=merged, body=body, timeout=timeout)


def download_file(url: str, dest: Path, timeout: int = 600) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
            while chunk := resp.read(1024 * 256):
                f.write(chunk)
    except urllib.error.URLError as e:
        raise SystemExit(f"download failed for {dest.name}: {e}") from None
