from __future__ import annotations

from django.urls import path

from .views import TelegramWebhookView

urlpatterns = [
    path("telegram/webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),
]
