from __future__ import annotations

import os

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Установить webhook для Telegram бота"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help=(
                "URL для webhook "
                "(например, https://yourdomain.com/api/telegram/webhook/)"
            ),
        )

    def handle(self, *args, **options):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            self.stdout.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN не установлен в .env")
            )
            return

        webhook_url = options.get("url")
        if not webhook_url:
            # Для локальной разработки можно использовать ngrok или подобный сервис
            self.stdout.write(
                self.style.WARNING(
                    "Укажите --url для webhook. "
                    "Для локальной разработки используйте ngrok: "
                    "ngrok http 8000, затем укажите полученный URL"
                )
            )
            return

        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        response = requests.post(api_url, json={"url": webhook_url}, timeout=10)

        if response.ok:
            data = response.json()
            if data.get("ok"):
                self.stdout.write(
                    self.style.SUCCESS(f"Webhook установлен: {webhook_url}")
                )
                info = requests.get(
                    f"https://api.telegram.org/bot{token}/getWebhookInfo", timeout=10
                ).json()
                if info.get("ok"):
                    webhook_info = info.get("result", {})
                    self.stdout.write(
                        f"Статус: {webhook_info.get('url', 'N/A')}\n"
                        f"Ожидает обновлений: "
                        f"{webhook_info.get('pending_update_count', 0)}"
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Ошибка: {data.get('description', 'Unknown error')}"
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"Ошибка HTTP: {response.status_code}")
            )
