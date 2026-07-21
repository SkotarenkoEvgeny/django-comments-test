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
        email="admin@test.com"
    )
