from __future__ import annotations

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Habit
from .permissions import IsOwner
from .serializers import HabitSerializer, PublicHabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками пользователя."""
    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitsListView(generics.ListAPIView):
    serializer_class = PublicHabitSerializer
    permission_classes = (AllowAny,)
    queryset = Habit.objects.filter(is_public=True)
