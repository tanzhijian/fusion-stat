import typing

import httpx

from .base import Downloader
from fusion_stat.models import Params
from fusion_stat.utils import unpack_params


class FotMob(Downloader):
    def __init__(
        self, client: httpx.AsyncClient, **kwargs: typing.Any
    ) -> None:
        super().__init__(client, **kwargs)
        self.base_url = "https://www.fotmob.com/api"

    async def get_competitions(self) -> httpx.Response:
        url = self.base_url + "/allLeagues"
        response = await self.get(url)
        return response

    async def get_competition(
        self, params: Params | dict[str, str]
    ) -> httpx.Response:
        params = unpack_params(params)
        url = self.base_url + "/leagues"
        httpx_params = {"id": params.fotmob_id}
        response = await self.get(url, params=httpx_params)
        return response

    async def get_team(
        self, params: Params | dict[str, str]
    ) -> httpx.Response:
        params = unpack_params(params)
        url = self.base_url + "/teams"
        httpx_params = {"id": params.fotmob_id}
        response = await self.get(url, params=httpx_params)
        return response

    async def get_member(
        self, params: Params | dict[str, str]
    ) -> httpx.Response:
        params = unpack_params(params)
        url = self.base_url + "/playerData"
        httpx_params = {"id": params.fotmob_id}
        response = await self.get(url, params=httpx_params)
        return response

    async def get_matches(self, date: str) -> httpx.Response:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        date = date.replace("-", "")
        url = self.base_url + "/matches"
        params = {"date": date}
        response = await self.get(url, params=params)
        return response

    async def get_match(
        self, params: Params | dict[str, str]
    ) -> httpx.Response:
        params = unpack_params(params)
        url = self.base_url + "/matchDetails"
        httpx_params = {"matchId": params.fotmob_id}
        response = await self.get(url, params=httpx_params)
        return response
