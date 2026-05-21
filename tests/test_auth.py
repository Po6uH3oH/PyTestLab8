from http import HTTPStatus
import pytest

from api.auth_api import login, verify_token, register
from assertions.assertion_base import assert_status_code, assert_schema, assert_error_detail
from models.auth_models import TokenSchema

class TestAuth:
    def test_login_success(self, unauth_client, registered_user):
        """
        Успешная авторизация (получение токена), 
        POST /api/auth/login
        """
        response = login(unauth_client, registered_user["username"], registered_user["password"])
        assert_status_code(response, HTTPStatus.OK)
        assert_schema(response, TokenSchema)

    def test_verify_token_success(self, auth_client):
        """
        Отправление полученного токена и проверка его валидности,
        POST /api/auth/verify
        """
        response = verify_token(auth_client)
        assert_status_code(response, HTTPStatus.OK)

    @pytest.mark.parametrize("user_type, pass_type", [
        ("invalid", "valid"),
        ("valid", "invalid"),
        ("empty", "empty"),
    ])
    def test_login_invalid_credentials(self, unauth_client, registered_user, user_type, pass_type):
        """
        Неуспешная авторизация с неверными данными,
        POST /api/auth/login
        """
        username = registered_user[
            "username"] if user_type == "valid" else "invalid_user_random" if user_type == "invalid" else ""
        password = registered_user[
            "password"] if pass_type == "valid" else "invalid_password_random" if pass_type == "invalid" else ""

        response = login(unauth_client, username, password)

        if user_type == "empty" or pass_type == "empty":
            assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.UNAUTHORIZED), \
                f"Ожидался 422 или 401, получен {response.status_code}"
        else:
            assert_status_code(response, HTTPStatus.UNAUTHORIZED)

    @pytest.mark.parametrize("missing_field", ["username", "email", "password"])
    def test_register_missing_fields(self, unauth_client, user_credentials, missing_field):
        """
        Регистрация без обязательных полей,
        POST /api/auth/register
        """
        payload = {
            "username": user_credentials["username"] + "_missing",
            "email": "missing_" + user_credentials["email"],
            "password": user_credentials["password"]
        }
        del payload[missing_field]

        response = unauth_client.post('/api/auth/register', json=payload)
        assert_status_code(response, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_error_detail(response, "Field required")

    def test_register_duplicate_username(self, unauth_client, registered_user):
        """
        Регистрация с уже существующим логином,
        POST /api/auth/register
        """
        response = register(unauth_client, registered_user["username"], "second_" + registered_user["email"], registered_user["password"])
        assert_status_code(response, HTTPStatus.BAD_REQUEST)

    @pytest.mark.parametrize("invalid_email", [
        "justtext",
        "@noadress.com",
        "nodomainname@.com",
        "nodot@com",
    ])
    def test_register_invalid_email_format(self, unauth_client, user_credentials, invalid_email):
        """
        Регистрация с некорректным форматом email,
        POST /api/auth/register
        """
        response = register(
            unauth_client,
            user_credentials["username"] + "_invalidemailtest",
            invalid_email,
            user_credentials["password"]
        )
        assert_status_code(response, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_error_detail(response, "valid email")

    def test_register_invalid_password_format(self, unauth_client, user_credentials):
        """
        Регистрация со слишком коротким паролем,
        POST /api/auth/register
        """
        response = register(
            unauth_client,
            user_credentials["username"] + "_invalidpasstest",
            "pass_" + user_credentials["email"],
            "111"
        )
        assert response.status_code in [HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST], \
               f"Регистрация не должна была произойти. Код: {response.status_code}"
