from __future__ import annotations

from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from habits.models import Habit

from .services import send_telegram_message, send_telegram_keyboard

User = get_user_model()


class BotHandler:
    """Обработчик команд Telegram бота."""

    def __init__(self, token: str):
        self.token = token
        self.user_states: dict[int, dict[str, Any]] = {}

    def handle_message(self, chat_id: int, text: str, username: str | None) -> None:
        """Обработка входящего сообщения."""
        # Проверяем состояние пользователя (создание привычки)
        if chat_id in self.user_states:
            state = self.user_states[chat_id]
            if state.get("action") == "creating_habit":
                self._handle_habit_creation(chat_id, text, state)
                return

        # Обработка команд
        if text.startswith("/"):
            command = text.split()[0].lower()
            if command == "/start":
                self._handle_start(chat_id, username)
            elif command == "/register":
                self._handle_register(chat_id, text, username)
            elif command == "/my_habits":
                self._handle_my_habits(chat_id)
            elif command == "/create_habit":
                self._handle_create_habit_start(chat_id)
            elif command == "/help":
                self._handle_help(chat_id)
            else:
                self._handle_unknown_command(chat_id)
        else:
            self._handle_unknown_command(chat_id)

    def _handle_start(self, chat_id: int, username: str | None) -> None:
        """Обработка команды /start."""
        try:
            user = None
            if username:
                try:
                    user = User.objects.get(username=username)
                    user.telegram_chat_id = chat_id
                    user.save(update_fields=["telegram_chat_id"])
                except User.DoesNotExist:
                    pass

            if user:
                message = (
                    f"Привет, {user.username}! 👋\n\n"
                    f"Добро пожаловать в трекер привычек!\n\n"
                    f"Доступные команды:\n"
                    f"/my_habits - мои привычки\n"
                    f"/create_habit - создать привычку\n"
                    f"/help - помощь\n\n"
                    f"Ваш Chat ID сохранён. Вы будете получать напоминания!"
                )
            else:
                message = (
                    f"Привет! 👋\n\n"
                    f"Добро пожаловать в трекер привычек!\n\n"
                    f"Для начала работы зарегистрируйтесь:\n"
                    f"/register <username> <password>\n\n"
                    f"Например:\n"
                    f"/register {username or 'myuser'} mypassword123\n\n"
                    f"Или используйте /help для списка команд."
                )

            keyboard = [
                [{"text": "📋 Мои привычки", "callback_data": "my_habits"}],
                [{"text": "➕ Создать привычку", "callback_data": "create_habit"}],
                [{"text": "❓ Помощь", "callback_data": "help"}],
            ]
            send_telegram_keyboard(
                token=self.token, chat_id=chat_id, text=message, keyboard=keyboard
            )
        except Exception as e:
            send_telegram_message(
                token=self.token,
                chat_id=chat_id,
                text=f"Ошибка: {e}",
            )

    def _handle_register(self, chat_id: int, text: str, username: str | None) -> None:
        """Обработка команды /register."""
        try:
            parts = text.split()
            if len(parts) < 3:
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text=(
                        "Использование: /register <username> <password>\n\n"
                        "Пример:\n"
                        "/register myuser mypassword123"
                    ),
                )
                return

            reg_username = parts[1]
            password = parts[2]

            if User.objects.filter(username=reg_username).exists():
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text=f"Пользователь '{reg_username}' уже существует.",
                )
                return

            user = User(username=reg_username)
            user.set_password(password)
            user.telegram_chat_id = chat_id
            user.save()

            message = (
                f"✅ Регистрация успешна!\n\n"
                f"Username: {reg_username}\n"
                f"Chat ID: {chat_id}\n\n"
                f"Теперь вы можете создавать привычки:\n"
                f"/create_habit"
            )
            send_telegram_message(token=self.token, chat_id=chat_id, text=message)
        except Exception as e:
            send_telegram_message(
                token=self.token,
                chat_id=chat_id,
                text=f"Ошибка при регистрации: {e}",
            )

    def _handle_my_habits(self, chat_id: int) -> None:
        """Показать список привычек пользователя."""
        try:
            user = User.objects.filter(telegram_chat_id=chat_id).first()
            if not user:
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text=(
                        "Вы не зарегистрированы. Используйте /register для регистрации."
                    ),
                )
                return

            habits = Habit.objects.filter(user=user).order_by("-created_at")[:10]

            if not habits:
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text="У вас пока нет привычек. Создайте первую: /create_habit",
                )
                return

            message = "📋 Ваши привычки:\n\n"
            for i, habit in enumerate(habits, 1):
                reward_text = ""
                if habit.reward:
                    reward_text = f"\nНаграда: {habit.reward}"
                elif habit.related_habit:
                    reward_text = f"\nНаграда: {habit.related_habit.action}"

                message += (
                    f"{i}. {habit.action}\n"
                    f"   🕐 {habit.time.strftime('%H:%M')}\n"
                    f"   📍 {habit.place}\n"
                    f"   ⏱ {habit.duration_seconds}с{reward_text}\n"
                    f"   🔄 Каждые {habit.periodicity} дн.\n\n"
                )

            send_telegram_message(token=self.token, chat_id=chat_id, text=message)
        except Exception as e:
            send_telegram_message(
                token=self.token,
                chat_id=chat_id,
                text=f"Ошибка: {e}",
            )

    def _handle_create_habit_start(self, chat_id: int) -> None:
        """Начать процесс создания привычки."""
        try:
            user = User.objects.filter(telegram_chat_id=chat_id).first()
            if not user:
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text=(
                        "Вы не зарегистрированы. Используйте /register для регистрации."
                    ),
                )
                return

            self.user_states[chat_id] = {
                "action": "creating_habit",
                "step": "action",
                "user": user,
            }

            message = (
                "Создание новой привычки 📝\n\n"
                "Шаг 1/5: Что вы будете делать?\n"
                "Напишите действие (например: 'выпить стакан воды')"
            )
            send_telegram_message(token=self.token, chat_id=chat_id, text=message)
        except Exception as e:
            send_telegram_message(
                token=self.token,
                chat_id=chat_id,
                text=f"Ошибка: {e}",
            )

    def _handle_habit_creation(self, chat_id: int, text: str, state: dict) -> None:
        """Обработка пошагового создания привычки."""
        try:
            step = state.get("step")
            user = state.get("user")

            if step == "action":
                state["action_text"] = text
                state["step"] = "place"
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text="Шаг 2/5: Где? (например: 'дома', 'в офисе')",
                )
            elif step == "place":
                state["place"] = text
                state["step"] = "time"
                send_telegram_message(
                    token=self.token,
                    chat_id=chat_id,
                    text=(
                        "Шаг 3/5: Во сколько? (формат: ЧЧ:ММ, например: 08:00)"
                    ),
                )
            elif step == "time":
                try:
                    time_obj = datetime.strptime(text, "%H:%M").time()
                    state["time"] = time_obj
                    state["step"] = "duration"
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text=(
                            "Шаг 4/5: Сколько времени займёт? "
                            "(в секундах, максимум 120, например: 60)"
                        ),
                    )
                except ValueError:
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text=(
                            "Неверный формат времени. "
                            "Используйте ЧЧ:ММ (например: 08:00)"
                        ),
                    )
            elif step == "duration":
                try:
                    duration = int(text)
                    if duration > 120:
                        send_telegram_message(
                            token=self.token,
                            chat_id=chat_id,
                            text="Максимум 120 секунд. Введите число от 1 до 120:",
                        )
                        return
                    state["duration"] = duration
                    state["step"] = "periodicity"
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text=(
                            "Шаг 5/5: Как часто? (дней, от 1 до 7, например: 1)"
                        ),
                    )
                except ValueError:
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text="Введите число (например: 60)",
                    )
            elif step == "periodicity":
                try:
                    periodicity = int(text)
                    if periodicity < 1 or periodicity > 7:
                        send_telegram_message(
                            token=self.token,
                            chat_id=chat_id,
                            text="Введите число от 1 до 7:",
                        )
                        return

                    # Создаём привычку
                    with transaction.atomic():
                        habit = Habit.objects.create(
                            user=user,
                            action=state["action_text"],
                            place=state["place"],
                            time=state["time"],
                            duration_seconds=state["duration"],
                            periodicity=periodicity,
                        )

                    message = (
                        f"✅ Привычка создана!\n\n"
                        f"Действие: {habit.action}\n"
                        f"Место: {habit.place}\n"
                        f"Время: {habit.time.strftime('%H:%M')}\n"
                        f"Длительность: {habit.duration_seconds}с\n"
                        f"Периодичность: каждые {habit.periodicity} дн.\n\n"
                        f"Вы будете получать напоминания!"
                    )
                    send_telegram_message(
                        token=self.token, chat_id=chat_id, text=message
                    )

                    # Удаляем состояние
                    del self.user_states[chat_id]
                except ValueError:
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text="Введите число от 1 до 7:",
                    )
                except Exception as e:
                    send_telegram_message(
                        token=self.token,
                        chat_id=chat_id,
                        text=f"Ошибка при создании: {e}",
                    )
                    del self.user_states[chat_id]
        except Exception as e:
            send_telegram_message(
                token=self.token,
                chat_id=chat_id,
                text=f"Ошибка: {e}",
            )
            if chat_id in self.user_states:
                del self.user_states[chat_id]

    def _handle_help(self, chat_id: int) -> None:
        """Показать справку."""
        message = (
            "📖 Справка по командам:\n\n"
            "/start - начать работу\n"
            "/register <username> <password> - регистрация\n"
            "/my_habits - список моих привычек\n"
            "/create_habit - создать новую привычку\n"
            "/help - эта справка\n\n"
            "Пример регистрации:\n"
            "/register myuser mypass123\n\n"
            "После регистрации используйте /create_habit для создания привычек."
        )
        send_telegram_message(token=self.token, chat_id=chat_id, text=message)

    def _handle_unknown_command(self, chat_id: int) -> None:
        """Обработка неизвестной команды."""
        message = (
            "Неизвестная команда. Используйте /help для списка команд."
        )
        send_telegram_message(token=self.token, chat_id=chat_id, text=message)
