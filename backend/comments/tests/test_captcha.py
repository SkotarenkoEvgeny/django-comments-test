import pytest

from django.core.cache import cache

from comments.models import Comment


@pytest.mark.django_db
def test_get_captcha(api_client):
    response = api_client.get("/api/captcha/")

    assert response.status_code == 200

    data = response.data

    assert "captcha_id" in data
    assert "image" in data
    assert "captcha_value" in data


@pytest.mark.django_db
def test_captcha_saved_in_cache(api_client):
    response = api_client.get("/api/captcha/")

    captcha_id = response.data["captcha_id"]
    captcha_value = response.data["captcha_value"]

    cached = cache.get(f"captcha:{captcha_id}")

    assert cached == captcha_value


@pytest.mark.django_db
def test_captcha_image(api_client):
    response = api_client.get("/api/captcha/")

    image = response.data["image"]

    assert image.startswith("data:image/png;base64,")


@pytest.mark.django_db
def test_expired_captcha(api_client):
    response = api_client.post(
        "/api/comments/",
        {
            "user_name": "Ivan",
            "email": "ivan@example.com",
            "text": "Hello",
            "captcha_id": "unknown",
            "captcha_value": "1234",
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "captcha_value" in response.data
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_wrong_captcha(api_client):
    captcha_id = "test"

    cache.set(
        f"captcha:{captcha_id}",
        "1234",
        timeout=300,
    )

    response = api_client.post(
        "/api/comments/",
        {
            "user_name": "Ivan",
            "email": "ivan@example.com",
            "text": "Hello",
            "captcha_id": captcha_id,
            "captcha_value": "9999",
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "captcha_value" in response.data
    assert Comment.objects.count() == 0

    # CAPTCHA не должна удалиться
    assert cache.get(f"captcha:{captcha_id}") == "1234"


@pytest.mark.django_db
def test_captcha_can_be_used_only_once(api_client):
    captcha_id = "captcha"

    cache.set(
        f"captcha:{captcha_id}",
        "1234",
        timeout=300,
    )

    data = {
        "user_name": "Ivan",
        "email": "ivan@example.com",
        "text": "Hello",
        "captcha_id": captcha_id,
        "captcha_value": "1234",
    }

    first = api_client.post(
        "/api/comments/",
        data,
        format="multipart",
    )

    second = api_client.post(
        "/api/comments/",
        data,
        format="multipart",
    )

    assert first.status_code == 201
    assert second.status_code == 400
    assert Comment.objects.count() == 1