from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        read_only_fields = (
            "id",
            "user",
            "last_reminded_at",
            "created_at",
            "updated_at",
        )
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration_seconds",
            "is_public",
            "last_reminded_at",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """Валидация данных привычки."""
        user = self.context["request"].user
        
        # Создаём временный объект для валидации
        if self.instance:
            # При обновлении объединяем текущие данные с новыми
            for key, value in attrs.items():
                setattr(self.instance, key, value)
            habit = self.instance
        else:
            # При создании создаём новый объект
            habit = Habit(user=user, **attrs)
        
        # Вызываем валидацию модели
        try:
            habit.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        
        return attrs

    def create(self, validated_data):
        """Создание новой привычки."""
        habit = Habit(user=self.context["request"].user, **validated_data)
        habit.full_clean()  # Валидация модели
        habit.save()
        return habit

    def update(self, instance, validated_data):
        """Обновление привычки."""
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.full_clean()  # Валидация модели
        instance.save()
        return instance


class PublicHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration_seconds",
        )
