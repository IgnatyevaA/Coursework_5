from __future__ import annotations

import os
import time

import requests
from django.core.management.base import BaseCommand

from telegram_bot.bot_handler import BotHandler


class Command(BaseCommand):
    help = (
        "Запустить polling для получения обновлений от Telegram "
        "(альтернатива webhook)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Timeout для long polling (по умолчанию 30 секунд)",
        )

    def handle(self, *args, **options):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            self.stdout.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN не установлен в .env")
            )
            return

        timeout = options["timeout"]
        api_url = f"https://api.telegram.org/bot{token}/getUpdates"
        offset = 0

        # Создаём обработчик бота
        bot_handler = BotHandler(token)

        self.stdout.write(
            self.style.SUCCESS(
                f"Запущен polling для бота (timeout={timeout}с). "
                "Нажмите Ctrl+C для остановки."
            )
        )

        try:
            while True:
                try:
                    response = requests.post(
                        api_url,
                        json={"offset": offset, "timeout": timeout},
                        timeout=timeout + 10,
                    )
                    data = response.json()

                    if not data.get("ok"):
                        self.stdout.write(
                            self.style.ERROR(f"Ошибка API: {data.get('description')}")
                        )
                        time.sleep(5)
                        continue

                    updates = data.get("result", [])
                    for update in updates:
                        offset = update["update_id"] + 1
                        self._handle_update(bot_handler, update)

                except requests.exceptions.RequestException as e:
                    self.stdout.write(
                        self.style.WARNING(f"Ошибка сети: {e}. Повтор через 5 сек...")
                    )
                    time.sleep(5)
                except KeyboardInterrupt:
                    self.stdout.write(self.style.SUCCESS("\nPolling остановлен"))
                    break
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Неожиданная ошибка: {e}")
                    )
                    time.sleep(5)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nPolling остановлен"))

    def _handle_update(self, bot_handler: BotHandler, update: dict):
        """Обработка одного обновления от Telegram."""
        if "message" not in update:
            return

        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        username = message.get("from", {}).get("username")

        if not chat_id:
            return

        try:
            bot_handler.handle_message(chat_id, text, username)
            self.stdout.write(
                f"Обработано сообщение от chat_id={chat_id}: {text[:50]}"
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ошибка при обработке сообщения: {e}")
            )
