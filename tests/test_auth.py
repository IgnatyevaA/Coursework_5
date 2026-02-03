from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_register_and_token(api_client):
    r = api_client.post(
        "/api/auth/register/",
        {"username": "new_user", "password": "pass12345"},
        format="json",
    )
    assert r.status_code == 201
    assert "id" in r.data

    t = api_client.post(
        "/api/auth/token/",
        {"username": "new_user", "password": "pass12345"},
        format="json",
    )
    assert t.status_code == 200
    assert "access" in t.data
