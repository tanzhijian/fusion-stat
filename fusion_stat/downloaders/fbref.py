import typing

import httpx

from .base import Downloader
from fusion_stat.models import Params
from fusion_stat.utils import unpack_params


class FBref(Downloader):
    def __init__(
        self, client: httpx.AsyncClient, **kwargs: typing.Any
    ) -> None:
        super().__init__(client, **kwargs)
        self.base_url = "https://fbref.com/en"

    async def get_competitions(self) -> httpx.Response:
        url = self.base_url + "/comps/"
        response = await self.get(url)
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

        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_team(
        self,
        params: Params | dict[str, str],
        season: str | None = None,
    ) -> httpx.Response:
        params = unpack_params(params)
        if season:
            path = "/squads" + f"/{params.fbref_id}/{season}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"
        else:
            path = "/squads" + f"/{params.fbref_id}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"

        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_member(
        self,
        params: Params | dict[str, str],
    ) -> httpx.Response:
        params = unpack_params(params)
        path = f"/players/{params.fbref_id}/"
        if params.fbref_path_name:
            path += params.fbref_path_name

        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_matches(self, date: str) -> httpx.Response:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        path = f"/matches/{date}"
        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_match(self, params: Params) -> httpx.Response:
        params = unpack_params(params)
        path = f"/matches/{params.fbref_id}"
        url = self.base_url + path

        response = await self.get(url)
        return response
