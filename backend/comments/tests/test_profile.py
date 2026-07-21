import pytest


@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    response = api_client.get("/api/profile/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_profile(api_client, user):
    token = api_client.post(
        "/api/token/",
        {
            "username": "admin",
            "password": "password123",
        },
        format="json",
    ).data["access"]

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    response = api_client.get("/api/profile/")

    assert response.status_code == 200

    assert response.data["username"] == "admin"
    assert response.data["email"] == "admin@test.com"


@pytest.mark.django_db
def test_profile_invalid_token(api_client):
    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer invalid-token"
    )

    response = api_client.get("/api/profile/")

    assert response.status_code == 401


