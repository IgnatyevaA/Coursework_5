from __future__ import annotations

from django.core.management.base import BaseCommand

from telegram_bot.services import send_telegram_message


class Command(BaseCommand):
    help = "Тест отправки сообщения в Telegram"

    def add_arguments(self, parser):
        parser.add_argument("chat_id", type=int, help="Telegram chat ID")
        parser.add_argument("message", type=str, help="Текст сообщения")

    def handle(self, *args, **options):
        chat_id = options["chat_id"]
        message = options["message"]

        try:
            send_telegram_message(chat_id, message)
            self.stdout.write(
                self.style.SUCCESS(f"Сообщение отправлено в chat_id={chat_id}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
