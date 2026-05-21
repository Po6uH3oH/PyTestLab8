from http import HTTPStatus

from api.auth_api import register, login
from api.profiles_api import get_my_profile, get_profiles, get_profile_by_id, delete_profile_by_id
from assertions.assertion_base import assert_status_code, assert_schema
from models.profile_models import ProfileSchema, ProfilesListSchema


class TestProfiles:
    def test_get_user_profile(self, auth_client):
        """
        Проверка метода получения информации о пользователе (User Profile),
        GET /api/profiles/me
        """
        response = get_my_profile(auth_client)
        assert_status_code(response, HTTPStatus.OK)
        assert_schema(response, ProfileSchema)

    def test_get_admin_profiles_list(self, admin_client):
        """
        Проверка метода получения информации об администраторе (или всеми профилями, доступного админу),
        GET /api/profiles/
        """
        response = get_profiles(admin_client)
        assert_status_code(response, HTTPStatus.OK)
        assert_schema(response, ProfilesListSchema)

    def test_get_user_profiles_list_role_limit(self, auth_client):
        """
        Проверка отображения списка пользователей без ролевого доступа,
        GET /api/profiles/
        """
        response = get_profiles(auth_client)
        assert_status_code(response, HTTPStatus.OK)
        assert_schema(response, ProfilesListSchema)

        data = response.json()
        assert len(data.get("profiles", [])) <= 1, f"Пользователь не должен видеть чужие профили в списке. Но было найдено профилей: {len(data)}. ДАнные с сервера: {data}"

    def test_user_cannot_access_other_profile(self, auth_client, unauth_client, admin_client, user_credentials):
        """
        Проверка доступа пользователя к другим аккаунтам,
        GET /api/profiles/{id}
        """
        other_username = user_credentials["username"] + "_other"
        other_email = "other_" + user_credentials["email"]
        register(unauth_client, other_username, other_email, user_credentials["password"])
        res = login(unauth_client, other_username, user_credentials["password"])
        other_user_id = res.json()["user"]["id"]

        try:
            response = get_profile_by_id(auth_client, other_user_id)
            assert response.status_code in [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND], \
                f"Ожидался код 403 или 404, получен {response.status_code}. Ответ сервера: {response.text}"
        finally:
            if admin_client and getattr(admin_client, 'headers', {}).get("Authorization"):
                delete_profile_by_id(admin_client, other_user_id)

    def test_user_cannot_delete_profile(self, auth_client, unauth_client, admin_client, user_credentials):
        """
        Проверка возможности удаления профиля у обычного пользователя,
        DELETE /api/profiles/{id}
        """
        username_to_delete = user_credentials["username"] + "_delete"
        email_to_delete = "delete_" + user_credentials["email"]
        register(unauth_client, username_to_delete, email_to_delete, user_credentials["password"])
        res = login(unauth_client, username_to_delete, user_credentials["password"])
        user_id_to_delete = res.json()["user"]["id"]

        try:
            response = delete_profile_by_id(auth_client, user_id_to_delete)
            assert response.status_code in [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND], \
                f"Ожидался 403 или 404, получен {response.status_code}. Ответ сервера: {response.text}"
        finally:
            if admin_client and getattr(admin_client, 'headers', {}).get("Authorization"):
                delete_profile_by_id(admin_client, user_id_to_delete)

    def test_admin_can_delete_profile(self, user_credentials, unauth_client, admin_client):
        """
        Проверка возможности удаления профилей у администратора,
        DELETE /api/profiles/{id}
        """
        username = user_credentials["username"] + "_delete"
        unique_email = "delete_" + user_credentials["email"]
        register(unauth_client, username, unique_email, user_credentials["password"])
        res = login(unauth_client, username, user_credentials["password"])
        user_id = res.json()["user"]["id"]

        response = delete_profile_by_id(admin_client, user_id)
        assert_status_code(response, HTTPStatus.OK)
