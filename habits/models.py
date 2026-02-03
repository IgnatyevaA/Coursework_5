from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits"
    )
    place = models.CharField(max_length=255)
    time = models.TimeField(help_text="Локальное время напоминания.")
    action = models.CharField(max_length=255)

    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_from",
        help_text="Приятная привычка как награда за полезную.",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(1), MaxValueValidator(7)),
        help_text="Периодичность в днях (1..7).",
    )
    reward = models.CharField(max_length=255, blank=True, default="")
    duration_seconds = models.PositiveSmallIntegerField(
        validators=(MaxValueValidator(120),),
        help_text="Время на выполнение в секундах (<=120).",
    )
    is_public = models.BooleanField(default=False)

    last_reminded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def clean(self):
        errors: dict[str, str] = {}

        if self.reward and self.related_habit_id:
            errors["reward"] = (
                "Нельзя указывать и вознаграждение, и связанную привычку."
            )
            errors["related_habit"] = (
                "Нельзя указывать и связанную привычку, и вознаграждение."
            )

        if (
            self.related_habit_id
            and self.related_habit
            and not self.related_habit.is_pleasant
        ):
            errors["related_habit"] = "Связанная привычка должна быть приятной."

        if (
            self.related_habit_id
            and self.related_habit
            and self.related_habit.user_id != self.user_id
        ):
            errors["related_habit"] = (
                "Связанная привычка должна принадлежать пользователю."
            )

        if self.is_pleasant and (self.reward or self.related_habit_id):
            errors["is_pleasant"] = (
                "У приятной привычки не может быть вознаграждения "
                "или связанной привычки."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.user_id}: {self.action} @ {self.time}"
