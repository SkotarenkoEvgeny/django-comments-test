import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="admin",
        password="password123",
        email="admin@test.com",
    )


@pytest.mark.django_db
def test_obtain_jwt_token(api_client, user):
    response = api_client.post(
        "/api/token/",
        {
            "username": "admin",
            "password": "password123",
        },
        format="json",
    )

    assert response.status_code == 200

    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_obtain_token_invalid_password(api_client, user):
    response = api_client.post(
        "/api/token/",
        {
            "username": "admin",
            "password": "wrong-password",
        },
        format="json",
    )

    assert response.status_code == 401

    assert "access" not in response.data


@pytest.mark.django_db
def test_refresh_token(api_client, user):
    response = api_client.post(
        "/api/token/",
        {
            "username": "admin",
            "password": "password123",
        },
        format="json",
    )

    refresh = response.data["refresh"]

    response = api_client.post(
        "/api/token/refresh/",
        {
            "refresh": refresh,
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_refresh_invalid_token(api_client):
    response = api_client.post(
        "/api/token/refresh/",
        {
            "refresh": "invalid-token",
        },
        format="json",
    )

    assert response.status_code == 401