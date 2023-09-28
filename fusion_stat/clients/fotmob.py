import typing

import httpx

from .base import Client
from fusion_stat.models import Params


class FotMob(Client):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(
            httpx_client_cls,
            base_url="https://www.fotmob.com/api",
            **kwargs,
        )

    async def get_competitions(self) -> httpx.Response:
        path = "/allLeagues"
        response = await self.get(path)
        return response

    async def get_competition(self, params: Params) -> httpx.Response:
        path = "/leagues"
        httpx_params = {"id": params.fotmob.id}
        response = await self.get(path, params=httpx_params)
        return response
