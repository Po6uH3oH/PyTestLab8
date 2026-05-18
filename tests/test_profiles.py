import os
from http import HTTPStatus
import pytest

from api.api_client import ApiClient
from api.auth_api import login
from api.profiles_api import get_my_profile, get_profiles
from assertions.assertion_base import assert_status_code

class TestProfiles:
    @pytest.fixture(scope='class')
    def user_client(self):
        client = ApiClient()
        username = os.getenv("TEST_USER_USERNAME")
        password = os.getenv("TEST_USER_PASSWORD")
        login_res = login(client, username, password)
        token = login_res.json().get("access_token") if login_res.status_code == 200 else None
        return ApiClient(token=token)

    @pytest.fixture(scope='class')
    def admin_client(self):
        client = ApiClient()
        username = os.getenv("TEST_ADMIN_USERNAME")
        password = os.getenv("TEST_ADMIN_PASSWORD")
        login_res = login(client, username, password)
        token = login_res.json().get("access_token") if login_res.status_code == 200 else None
        return ApiClient(token=token)

    def test_get_user_profile(self, user_client):
        """
        Проверка метода получения информации о пользователе (User Profile),
        GET /api/profiles/me
        """
        response = get_my_profile(user_client)
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert isinstance(data, dict), "Ожидался JSON объект профиля"

    def test_get_admin_profiles_list(self, admin_client):
        """
        Проверка метода получения информации об администраторе (или всеми профилями, доступного админу),
        GET /api/profiles/
        """
        response = get_profiles(admin_client)
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert data is not None, "Список профилей (или объект) пустой"
