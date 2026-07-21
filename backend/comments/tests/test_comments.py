import pytest

from comments.models import Comment
from comments.tests.factories import CommentFactory

from django.core.cache import cache

@pytest.mark.django_db
def test_get_comments(api_client):
    response = api_client.get("/api/comments/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_comments(api_client):
    CommentFactory.create_batch(3)

    response = api_client.get("/api/comments/")

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3


@pytest.mark.django_db
def test_comment_fields(api_client):
    comment = CommentFactory()

    response = api_client.get("/api/comments/")

    result = response.data["results"][0]

    assert result["id"] == comment.id
    assert result["user_name"] == comment.user_name
    assert result["email"] == comment.email
    assert result["text"] == comment.text


@pytest.mark.django_db
def test_create_comment(api_client):
    captcha_id = "test-captcha"

    cache.set(
        f"captcha:{captcha_id}",
        "1234",
        timeout=300,
    )

    data = {
        "user_name": "Ivan",
        "email": "ivan@test.com",
        "home_page": "https://example.com",
        "text": "<strong>Hello</strong>",
        "captcha_id": captcha_id,
        "captcha_value": "1234",
    }

    response = api_client.post(
        "/api/comments/",
        data,
        format="multipart",
    )

    assert response.status_code == 201
    assert Comment.objects.count() == 1

    comment = Comment.objects.first()

    assert comment.user_name == "Ivan"
    assert comment.email == "ivan@test.com"
    assert comment.text == "<strong>Hello</strong>"
    assert cache.get(f"captcha:{captcha_id}") is None


@pytest.mark.django_db
def test_invalid_captcha(api_client):
    captcha_id = "captcha"

    cache.set(
        f"captcha:{captcha_id}",
        "1234",
    )

    response = api_client.post(
        "/api/comments/",
        {
            "user_name": "Ivan",
            "email": "ivan@test.com",
            "text": "Hello",

            "captcha_id": captcha_id,
            "captcha_value": "9999",
        },
        format="multipart",
    )

    assert response.status_code == 400

    assert "captcha_value" in response.data

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_expired_captcha(api_client):
    response = api_client.post(
        "/api/comments/",
        {
            "user_name": "Ivan",
            "email": "ivan@test.com",
            "text": "Hello",

            "captcha_id": "unknown",
            "captcha_value": "1234",
        },
        format="multipart",
    )

    assert response.status_code == 400

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_get_empty_comments(api_client):
    response = api_client.get("/api/comments/")

    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_get_comments(api_client):
    CommentFactory.create_batch(3)

    response = api_client.get("/api/comments/")

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3

