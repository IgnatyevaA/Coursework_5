from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import TelegramChatIdSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)


class TelegramChatIdUpdateView(generics.UpdateAPIView):
    serializer_class = TelegramChatIdSerializer

    def get_object(self):
        return self.request.user
