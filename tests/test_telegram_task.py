from __future__ import annotations

import datetime as dt

import pytest
from django.utils import timezone

from habits.models import Habit
from telegram_bot.tasks import send_habits_reminders


class _Resp:
    def __init__(self, ok=True, data=None):
        self.ok = ok
        self._data = data or {"ok": True, "result": {"message_id": 1}}

    def json(self):
        return self._data


@pytest.mark.django_db
def test_send_habits_reminders_sends_and_updates_timestamp(
    monkeypatch, user_factory
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    user = user_factory(username="tg", telegram_chat_id=123456)

    habit = Habit.objects.create(
        user=user,
        place="home",
        time=dt.time(12, 30),
        action="walk",
        periodicity=1,
        duration_seconds=60,
    )

    fixed_now = timezone.make_aware(dt.datetime(2026, 1, 1, 12, 30, 0))
    monkeypatch.setattr(timezone, "now", lambda: fixed_now)

    import telegram_bot.services as services

    monkeypatch.setattr(services.requests, "post", lambda *a, **k: _Resp())

    sent = send_habits_reminders()
    assert sent == 1

    habit.refresh_from_db()
    assert habit.last_reminded_at is not None


@pytest.mark.django_db
def test_send_habits_reminders_respects_periodicity(monkeypatch, user_factory):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    user = user_factory(username="tg2", telegram_chat_id=123457)

    fixed_now = timezone.make_aware(dt.datetime(2026, 1, 3, 12, 30, 0))
    monkeypatch.setattr(timezone, "now", lambda: fixed_now)

    habit = Habit.objects.create(
        user=user,
        place="home",
        time=dt.time(12, 30),
        action="walk",
        periodicity=7,
        duration_seconds=60,
        last_reminded_at=timezone.make_aware(dt.datetime(2026, 1, 1, 12, 30, 0)),
    )

    import telegram_bot.services as services

    monkeypatch.setattr(services.requests, "post", lambda *a, **k: _Resp())

    sent = send_habits_reminders()
    assert sent == 0
    habit.refresh_from_db()
    assert habit.last_reminded_at.date() == dt.date(2026, 1, 1)
