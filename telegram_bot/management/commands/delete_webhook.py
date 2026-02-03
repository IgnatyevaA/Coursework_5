from __future__ import annotations

import os

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Удалить webhook для Telegram бота"

    def handle(self, *args, **options):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            self.stdout.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN не установлен в .env")
            )
            return

        api_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.post(
            api_url, json={"drop_pending_updates": True}, timeout=10
        )

        if response.ok:
            data = response.json()
            if data.get("ok"):
                self.stdout.write(self.style.SUCCESS("Webhook удалён"))
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
