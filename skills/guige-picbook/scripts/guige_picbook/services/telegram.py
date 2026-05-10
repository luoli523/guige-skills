"""Telegram service for sending generated PDF files."""

from __future__ import annotations

from pathlib import Path

import httpx

from ..utils.config import Settings


class TelegramService:
    """Send generated files through the Telegram Bot API."""

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, settings: Settings):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        if not self.token or not self.chat_id:
            raise ValueError(
                "Telegram is not configured. Set these in "
                "~/.guige-skills/guige-picbook/.env or .guige-skills/guige-picbook/.env:\n"
                "  TELEGRAM_BOT_TOKEN=your_bot_token\n"
                "  TELEGRAM_CHAT_ID=your_chat_id"
            )
        self.base_url = self.API_BASE.format(token=self.token)

    async def send_message(self, text: str, parse_mode: str = "HTML") -> dict:
        """发送文本消息"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/sendMessage",
                data={"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode},
            )
            resp.raise_for_status()
            return resp.json()

    async def send_document(
        self, file_path: str, caption: str = "", parse_mode: str = "HTML"
    ) -> dict:
        """发送文件（PDF 等）"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    f"{self.base_url}/sendDocument",
                    data={
                        "chat_id": self.chat_id,
                        "caption": caption,
                        "parse_mode": parse_mode,
                    },
                    files={"document": (Path(file_path).name, f, "application/pdf")},
                )
            resp.raise_for_status()
            return resp.json()
