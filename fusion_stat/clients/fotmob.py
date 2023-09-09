import typing

import httpx

from .base import JSONClient


class FotMob(JSONClient):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(
            client_cls,
            base_url="https://www.fotmob.com/api",
            **kwargs,
        )

    async def get_competition(self, code: str) -> typing.Any:
        path = "/leagues"
        params = {"id": code}
        json = await self.get(path, params=params)
        return json
