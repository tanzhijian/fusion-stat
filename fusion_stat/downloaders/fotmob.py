import typing

import httpx

from .base import Downloader


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

    async def get_competition(self, id: str) -> httpx.Response:
        url = self.base_url + "/leagues"
        params = {"id": id}
        response = await self.get(url, params=params)
        return response

    async def get_team(self, id: str) -> httpx.Response:
        url = self.base_url + "/teams"
        params = {"id": id}
        response = await self.get(url, params=params)
        return response

    async def get_member(self, id: str) -> httpx.Response:
        url = self.base_url + "/playerData"
        params = {"id": id}
        response = await self.get(url, params=params)
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

    async def get_match(self, id: str) -> httpx.Response:
        url = self.base_url + "/matchDetails"
        params = {"matchId": id}
        response = await self.get(url, params=params)
        return response
