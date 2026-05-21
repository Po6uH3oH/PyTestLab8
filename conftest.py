import logging
import os
import time

import pytest
from dotenv import load_dotenv

from api.api_client import ApiClient
from api.profiles_api import delete_profile_by_id
from api.auth_api import register, login
from utilities.logger_utils import logger

def pytest_configure(config):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path=".env")
    path = "logs/"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_handler = logging.FileHandler(path + "info.log", "w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(lineno)d: %(asctime)s %(message)s"))

    custom_logger = logging.getLogger("custom_logger")
    custom_logger.setLevel(logging.INFO)
    custom_logger.addHandler(file_handler)

def pytest_runtest_setup(item):
    logger.info(f"Запуск теста: {item.name}:")

@pytest.fixture(scope='session')
def unauth_client():
    """Клиент без авторизации (для регистрации и логина)"""
    return ApiClient()

@pytest.fixture(scope='session')
def admin_client():
    """Клиент администратора"""
    client = ApiClient()
    username = os.getenv("TEST_ADMIN_USERNAME", "admin")
    password = os.getenv("TEST_ADMIN_PASSWORD", "admin")
    res = login(client, username, password)

    auth_token = None
    if res.status_code == 200:
        auth_token = res.json().get("access_token")

    return ApiClient(token=auth_token)

@pytest.fixture(scope='function')
def user_credentials():
    return {
        "username": os.getenv("TEMP_USERNAME", "TestUser"),
        "email": os.getenv("TEMP_EMAIL", "testemail@example.com"),
        "password": os.getenv("TEMP_PASSWORD", "TestPass123")
    }

@pytest.fixture(scope='function')
def registered_user(unauth_client, admin_client, user_credentials):
    """
    Создание тестового пользователя который удаляется после теста
    """
    username = user_credentials["username"]
    email = user_credentials["email"]
    password = user_credentials["password"]

    # Перестраховка от залагавшего тестового пользователя на сервере
    if admin_client and getattr(admin_client, 'headers', {}).get("Authorization"):
        old_login = login(unauth_client, username, password)
        if old_login.status_code == 200:
            old_id = old_login.json()["user"]["id"]
            delete_profile_by_id(admin_client, old_id)

    register_res = register(unauth_client, username, email, password)
    assert register_res.status_code == 200, f"Не удалось зарегистрировать тестового пользователя: {register_res.text}"

    login_res = login(unauth_client, username, password)
    assert login_res.status_code == 200, f"Не удалось авторизовать тестового пользователя"
    user_id = login_res.json()["user"]["id"]

    user_info = user_credentials.copy()
    user_info["id"] = user_id

    yield user_info

    if admin_client and getattr(admin_client, 'headers', {}).get("Authorization"):
        delete_profile_by_id(admin_client, user_id)

@pytest.fixture(scope='function')
def auth_client(unauth_client, registered_user):
    """
    Авторизуется под созданным тестовым пользователем и возвращает авторизованный ApiClient.
    """
    login_res = login(unauth_client, registered_user["username"], registered_user["password"])
    assert login_res.status_code == 200, f"Не удалось авторизовать тестового пользователя"

    token = login_res.json()["access_token"]

    yield ApiClient(token=token)

def pytest_runtest_teardown(item, nextitem):
    time.sleep(1)

