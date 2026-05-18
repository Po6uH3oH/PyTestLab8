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
