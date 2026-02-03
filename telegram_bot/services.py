from __future__ import annotations

from typing import Any

import requests


class TelegramError(RuntimeError):
    pass


def send_telegram_message(*, token: str, chat_id: int, text: str) -> dict[str, Any]:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    data = response.json()
    if not response.ok or not data.get("ok", False):
        raise TelegramError(f"Telegram API error: {data}")
    return data


def send_telegram_keyboard(
    *, token: str, chat_id: int, text: str, keyboard: list[list[dict[str, str]]]
) -> dict[str, Any]:
    """Отправить сообщение с inline клавиатурой."""
    reply_markup = {"inline_keyboard": keyboard}
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
        },
        timeout=10,
    )
    data = response.json()
    if not response.ok or not data.get("ok", False):
        raise TelegramError(f"Telegram API error: {data}")
    return data
