from __future__ import annotations

from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "time",
        "place",
        "is_pleasant",
        "related_habit",
        "periodicity",
        "duration_seconds",
        "is_public",
    )
    list_filter = ("is_public", "is_pleasant", "periodicity")
    search_fields = ("action", "place", "user__username")
