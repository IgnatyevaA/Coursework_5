from __future__ import annotations

import datetime as dt

import pytest

from habits.models import Habit


@pytest.mark.django_db
def test_cannot_set_reward_and_related_habit(auth_client, user_factory):
    user = user_factory(username="v1")
    client = auth_client(user=user)

    pleasant = Habit.objects.create(
        user=user,
        place="home",
        time=dt.time(10, 0),
        action="bath",
        is_pleasant=True,
        periodicity=1,
        duration_seconds=60,
    )

    r = client.post(
        "/api/habits/",
        {
            "place": "street",
            "time": "10:00:00",
            "action": "walk",
            "is_pleasant": False,
            "related_habit": pleasant.id,
            "reward": "dessert",
            "periodicity": 1,
            "duration_seconds": 60,
        },
        format="json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
def test_duration_max_120_seconds(auth_client, user_factory):
    user = user_factory(username="v2")
    client = auth_client(user=user)
    r = client.post(
        "/api/habits/",
        {
            "place": "home",
            "time": "10:00:00",
            "action": "x",
            "is_pleasant": False,
            "periodicity": 1,
            "duration_seconds": 121,
        },
        format="json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
def test_related_habit_must_be_pleasant(auth_client, user_factory):
    user = user_factory(username="v3")
    client = auth_client(user=user)
    not_pleasant = Habit.objects.create(
        user=user,
        place="home",
        time=dt.time(10, 0),
        action="not pleasant",
        is_pleasant=False,
        periodicity=1,
        duration_seconds=60,
    )
    r = client.post(
        "/api/habits/",
        {
            "place": "home",
            "time": "11:00:00",
            "action": "useful",
            "is_pleasant": False,
            "related_habit": not_pleasant.id,
            "periodicity": 1,
            "duration_seconds": 60,
        },
        format="json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward_or_related(auth_client, user_factory):
    user = user_factory(username="v4")
    client = auth_client(user=user)
    r = client.post(
        "/api/habits/",
        {
            "place": "home",
            "time": "10:00:00",
            "action": "bath",
            "is_pleasant": True,
            "reward": "x",
            "periodicity": 1,
            "duration_seconds": 60,
        },
        format="json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
def test_periodicity_cannot_be_more_than_7_days(auth_client, user_factory):
    user = user_factory(username="v5")
    client = auth_client(user=user)
    r = client.post(
        "/api/habits/",
        {
            "place": "home",
            "time": "10:00:00",
            "action": "x",
            "is_pleasant": False,
            "periodicity": 8,
            "duration_seconds": 60,
        },
        format="json",
    )
    assert r.status_code == 400
