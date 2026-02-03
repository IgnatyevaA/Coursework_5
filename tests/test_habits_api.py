from __future__ import annotations

import datetime as dt

import pytest

from habits.models import Habit


@pytest.mark.django_db
def test_habits_pagination_page_size_5(auth_client, user_factory):
    user = user_factory(username="pager")
    client = auth_client(user=user)
    for i in range(6):
        Habit.objects.create(
            user=user,
            place="home",
            time=dt.time(12, 0),
            action=f"do {i}",
            periodicity=1,
            duration_seconds=60,
        )

    r = client.get("/api/habits/")
    assert r.status_code == 200
    assert r.data["count"] == 6
    assert len(r.data["results"]) == 5
    assert r.data["next"] is not None


@pytest.mark.django_db
def test_habit_crud_only_owner(auth_client, user_factory):
    u1 = user_factory(username="u1")
    u2 = user_factory(username="u2")
    c1 = auth_client(user=u1)
    c2 = auth_client(user=u2)

    created = c1.post(
        "/api/habits/",
        {
            "place": "park",
            "time": "12:30:00",
            "action": "walk",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "dessert",
            "duration_seconds": 60,
            "is_public": False,
        },
        format="json",
    )
    assert created.status_code == 201
    habit_id = created.data["id"]

    # Другой пользователь не должен видеть/править привычку
    assert c2.get(f"/api/habits/{habit_id}/").status_code == 404
    assert (
        c2.patch(f"/api/habits/{habit_id}/", {"place": "x"}, format="json").status_code
        == 404
    )
    assert c2.delete(f"/api/habits/{habit_id}/").status_code == 404


@pytest.mark.django_db
def test_public_habits_list_allow_any(api_client, user_factory):
    user = user_factory(username="pub")
    Habit.objects.create(
        user=user,
        place="home",
        time=dt.time(8, 0),
        action="read",
        periodicity=1,
        duration_seconds=60,
        is_public=True,
    )
    r = api_client.get("/api/habits/public/")
    assert r.status_code == 200
    assert r.data["count"] == 1
