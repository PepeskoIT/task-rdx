import logging

import aiohttp

from envs import (APP_LOGGER_NAME, CORE_API_PASSWORD, CORE_API_PORT,
                  CORE_API_URL, CORE_API_USER, NETWORK_API_PASSWORD,
                  NETWORK_API_PORT, NETWORK_API_URL, NETWORK_API_USER)

logger = logging.getLogger(APP_LOGGER_NAME)


class AsyncApiClient:

    def __init__(self, url, port, login, password) -> None:
        self.url = url
        self.port = port
        self.login = login
        self.password = password
        self.session = None

    def __getattr__(self, attr):
        assert self.session is not None
        return getattr(self.session, attr)

    def prepare_session(self):
        self.session = aiohttp.ClientSession(
            f"https://{self.url}:{self.port}",
            auth=aiohttp.BasicAuth(self.login, self.password, 'utf-8'),
            )

    async def close(self):
        await self.session.close()
        self.session = None


core_api = AsyncApiClient(
    url=CORE_API_URL, port=CORE_API_PORT,
    login=CORE_API_USER, password=CORE_API_PASSWORD
)

network_api = AsyncApiClient(
    url=NETWORK_API_URL, port=NETWORK_API_PORT, login=NETWORK_API_USER,
    password=NETWORK_API_PASSWORD
)
