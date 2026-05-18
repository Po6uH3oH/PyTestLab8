import os
from httpx import Client, Response
from utilities.logger_utils import logger

class ApiClient(Client):
    def __init__(self, token=None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        super().__init__(base_url=f"https://{os.getenv('RESOURCE_URL')}", headers=headers)

    def request(self, method, url, **kwargs) -> Response:
        if os.getenv("USE_LOGS") == 'True':
            logger.info(f'{method} {url}')
        return super().request(method, url, **kwargs)
