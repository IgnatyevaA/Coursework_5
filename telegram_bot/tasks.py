from __future__ import annotations

import os

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from habits.models import Habit

from .services import TelegramError, send_telegram_message

User = get_user_model()


def _build_text(habit: Habit) -> str:
    reward = habit.reward
    if habit.related_habit:
        reward = f"Приятная привычка: {habit.related_habit.action}"
    if reward:
        reward = f"\nНаграда: {reward}"
    return (
        f"Напоминание о привычке:\n"
        f"Действие: {habit.action}\n"
        f"Место: {habit.place}\n"
        f"Время: {habit.time.strftime('%H:%M')}{reward}"
    )


@shared_task
def send_habits_reminders() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return 0

    now = timezone.localtime(timezone.now())
    today = now.date()
    sent = 0

    habits = (
        Habit.objects.select_related("related_habit", "user")
        .filter(user__telegram_chat_id__isnull=False)
        .all()
    )

    for habit in habits:
        if habit.time.hour != now.time().hour or habit.time.minute != now.time().minute:
            continue

        if habit.last_reminded_at is not None:
            last = timezone.localtime(habit.last_reminded_at).date()
            if (today - last).days < habit.periodicity:
                continue

        try:
            send_telegram_message(
                token=token,
                chat_id=int(habit.user.telegram_chat_id),
                text=_build_text(habit),
            )
        except TelegramError:
            # Чтобы задача не падала целиком из-за одного пользователя.
            continue

        with transaction.atomic():
            Habit.objects.filter(pk=habit.pk).update(last_reminded_at=now)
        sent += 1

    return sent
