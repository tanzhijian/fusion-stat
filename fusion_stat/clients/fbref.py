import typing

import httpx

from .base import Client


class FBref(Client):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(
            httpx_client_cls,
            base_url="https://fbref.com/en",
            **kwargs,
        )

    async def get_competitions(self) -> httpx.Response:
        path = "/comps/"
        response = await self.get(path)
        return response
