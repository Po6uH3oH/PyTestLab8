from typing import Type
from pydantic import BaseModel

class LogMsg:
    def __init__(self, where, response):
        self._msg = ""
        self._response = response
        self._where = where

    def add_request_url(self):
        self._msg += f"Содержимое отправляемого запроса:\n\tURL: {self._response.request.url}\n\tmethod: {self._response.request.method}\n\theaders: {dict(self._response.request.headers)}\n"
        if hasattr(self._response.request, 'content') and self._response.request.read():
            self._msg += f"\tbody: {self._response.request.read()}\n"
        return self

    def add_response_info(self):
        self._msg += f"Тело ответа:\n\t{self._response.content}\n"
        return self

    def get_message(self):
        return self._msg

class CodeLogMsg(LogMsg):
    def __init__(self, response):
        super().__init__('В КОДЕ ОТВЕТА', response)

    def add_compare_result(self, exp, act):
        self._msg += f"{self._where} \n\tожидался код: {exp}\n\tполученный код: {act}\n"
        return self

def assert_status_code(response, expected_code):
    assert expected_code == response.status_code, CodeLogMsg(response) \
        .add_compare_result(expected_code, response.status_code) \
        .add_request_url() \
        .add_response_info() \
        .get_message()

def assert_schema(response, model: Type[BaseModel]):
    body = response.json()
    if isinstance(body, list):
        for item in body:
            model.model_validate(item, strict=False)
    else:
        model.model_validate(body, strict=False)

def assert_error_detail(response, expected_detail):
    data = response.json()
    assert "detail" in data, f"Нет ключа 'detail' в ответе: {data}"
    actual_detail = data["detail"]
    if isinstance(actual_detail, str):
        assert expected_detail in actual_detail, f"Ожидаемая ошибка '{expected_detail}' не найдена в '{actual_detail}'"
    elif isinstance(actual_detail, list):
        msg_list = [err.get("msg", "") for err in actual_detail]
        assert any(expected_detail in msg for msg in msg_list), f"Ожидаемая ошибка '{expected_detail}' не найдена в {msg_list}"
