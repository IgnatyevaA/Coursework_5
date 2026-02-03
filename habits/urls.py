from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitsListView

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("habits/public/", PublicHabitsListView.as_view(), name="habits_public"),
    path("", include(router.urls)),
]
