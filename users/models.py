from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="Chat ID пользователя в Telegram для отправки напоминаний.",
    )
