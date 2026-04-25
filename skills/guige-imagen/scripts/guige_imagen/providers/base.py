from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error ({error.code}): {detail}") from error


def download_bytes(url: str, timeout: int = 300) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Image download failed ({error.code}): {detail}") from error


def post_multipart(
    url: str,
    headers: dict[str, str],
    fields: dict[str, str],
    files: list[tuple[str, str, str, bytes]],
    timeout: int = 300,
) -> dict[str, Any]:
    boundary = "----guige-imagen-boundary"
    chunks: list[bytes] = []

    for key, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )

    for field_name, filename, mime_type, data in files:
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                (
                    f'Content-Disposition: form-data; name="{field_name}"; '
                    f'filename="{filename}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {mime_type}\r\n\r\n".encode("ascii"),
                data,
                b"\r\n",
            ]
        )

    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    body = b"".join(chunks)
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            **headers,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error ({error.code}): {detail}") from error
