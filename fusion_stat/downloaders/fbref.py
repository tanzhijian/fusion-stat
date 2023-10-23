import typing

import httpx

from .base import Downloader


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
        self, id: str, season: str | None = None, **kwargs: str
    ) -> httpx.Response:
        if season:
            path = "/comps" + f"/{id}/{season}"
            if path_name := kwargs.get("path_name"):
                path += f"/{season}-{path_name}-Stats"
        else:
            path = "/comps" + f"/{id}"
            if path_name := kwargs.get("path_name"):
                path += f"/{path_name}-Stats"

        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_team(
        self, id: str, season: str | None = None, **kwargs: str
    ) -> httpx.Response:
        if season:
            path = "/squads" + f"/{id}/{season}"
            if path_name := kwargs.get("path_name"):
                path += f"/{path_name}-Stats"
        else:
            path = "/squads" + f"/{id}"
            if path_name := kwargs.get("path_name"):
                path += f"/{path_name}-Stats"

        url = self.base_url + path

        response = await self.get(url)
        return response

    async def get_member(self, id: str, **kwargs: str) -> httpx.Response:
        path = f"/players/{id}/"
        if path_name := kwargs.get("path_name"):
            path += path_name

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

    async def get_match(self, id: str) -> httpx.Response:
        path = f"/matches/{id}"
        url = self.base_url + path

        response = await self.get(url)
        return response
