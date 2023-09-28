import typing

import httpx

from .base import Client
from fusion_stat.models import Params
from fusion_stat.utils import unpack_params


class FBref(Client):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
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

    async def get_competition(
        self,
        params: Params | dict[str, str],
        season: str | None = None,
    ) -> httpx.Response:
        params = unpack_params(params)
        if season:
            path = "/comps" + f"/{params.fbref_id}/{season}"
            if params.fbref_path_name:
                path += f"/{season}-{params.fbref_path_name}-Stats"
        else:
            path = "/comps" + f"/{params.fbref_id}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"

        response = await self.get(path)
        return response
