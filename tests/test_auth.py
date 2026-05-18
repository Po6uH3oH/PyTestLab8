import os
from http import HTTPStatus
import pytest

from api.api_client import ApiClient
from api.auth_api import login, verify_token
from assertions.assertion_base import assert_status_code, assert_schema
from models.auth_models import TokenSchema

class TestAuth:
    @pytest.fixture(scope='class')
    def client(self):
        return ApiClient()

    def test_login_success(self, client):
        """
        Успешная авторизация (получение токена), 
        POST /api/auth/login
        """
        username = os.getenv("TEST_USER_USERNAME")
        password = os.getenv("TEST_USER_PASSWORD")

        response = login(client, username, password)

        assert_status_code(response, HTTPStatus.OK)
        assert_schema(response, TokenSchema)

    def test_verify_token_success(self, client):
        """
        Отправление полученного токена и проверка его валидности,
        POST /api/auth/verify
        """
        username = os.getenv("TEST_USER_USERNAME")
        password = os.getenv("TEST_USER_PASSWORD")

        login_response = login(client, username, password)
        token = login_response.json().get("access_token")

        auth_client = ApiClient(token=token)
        response = verify_token(auth_client)

        assert_status_code(response, HTTPStatus.OK)

    def test_login_invalid_credentials(self, client):
        """
        Неуспешная авторизация с неверными данными
        """
        response = login(client, "invalid_user", "invalid_password")
        assert response.status_code != HTTPStatus.OK
