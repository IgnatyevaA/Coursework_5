from __future__ import annotations

import json
import os

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .bot_handler import BotHandler
from .services import send_telegram_message

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):
    """Обработчик webhook от Telegram для получения обновлений."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            return JsonResponse(
                {"ok": False, "error": "Bot token not configured"}, status=500
            )

        # Обработка обновления от Telegram
        if "message" in data:
            message = data["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "").strip()
            username = message.get("from", {}).get("username")

            if not chat_id:
                return JsonResponse({"ok": True})

            # Используем новый обработчик бота
            bot_handler = BotHandler(token)
            try:
                bot_handler.handle_message(chat_id, text, username)
            except Exception:
                # Игнорируем ошибки, чтобы не ломать webhook
                pass

        return JsonResponse({"ok": True})

    def _handle_start_command(self, token: str, chat_id: int, username: str | None):
        """Обработка команды /start: сохранение chat_id пользователя."""
        try:
            # Пытаемся найти пользователя по username, если он указан
            user = None
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    pass

            # Если пользователь не найден, отправляем инструкцию
            if not user:
                message = (
                    f"Привет! 👋\n\n"
                    f"Ваш Telegram Chat ID: {chat_id}\n\n"
                    f"Чтобы получать напоминания о привычках:\n"
                    f"1. Зарегистрируйтесь в системе\n"
                    f"2. Укажите этот Chat ID в настройках профиля\n"
                    f"3. Создайте привычки с указанием времени\n\n"
                    f"Или, если у вас уже есть аккаунт с username '{username}', "
                    f"ваш Chat ID будет сохранён автоматически."
                )
            else:
                # Сохраняем chat_id для найденного пользователя
                user.telegram_chat_id = chat_id
                user.save(update_fields=["telegram_chat_id"])
                message = (
                    f"Отлично, {user.username}! ✅\n\n"
                    f"Ваш Telegram Chat ID ({chat_id}) сохранён.\n"
                    f"Теперь вы будете получать напоминания о привычках!"
                )

            send_telegram_message(token=token, chat_id=chat_id, text=message)
        except Exception:
            # Игнорируем ошибки, чтобы не ломать webhook
            pass

    def _handle_unknown_command(self, token: str, chat_id: int):
        """Обработка неизвестных команд."""
        try:
            message = (
                "Неизвестная команда. Используйте /start для начала работы."
            )
            send_telegram_message(token=token, chat_id=chat_id, text=message)
        except Exception:
            pass
