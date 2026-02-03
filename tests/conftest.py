from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_factory(db):
    def _factory(**kwargs):
        password = kwargs.pop("password", "pass12345")
        user = User.objects.create_user(password=password, **kwargs)
        user.raw_password = password  # type: ignore[attr-defined]
        return user

    return _factory


@pytest.fixture
def auth_client(api_client: APIClient, user_factory):
    def _factory(user=None, **kwargs) -> APIClient:
        if user is None:
            user = user_factory(username=kwargs.get("username", "u1"))

        response = api_client.post(
            "/api/auth/token/",
            {"username": user.username, "password": user.raw_password},
            format="json",
        )
        assert response.status_code == 200
        token = response.data["access"]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    return _factory
