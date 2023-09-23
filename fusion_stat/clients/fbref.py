import httpx
from httpx._types import ProxiesTypes

from .base import Client
from fusion_stat.config import COMPETITIONS_INDEX


class FBref(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(
            client_cls,
            base_url="https://fbref.com/en",
            proxies=proxies,
        )

    async def get_competitions(self) -> httpx.Response:
        path = "/comps/"
        response = await self.get(path)
        return response

    async def get_competition(
        self,
        id: str,
        season: str | None = None,
    ) -> httpx.Response:
        index = COMPETITIONS_INDEX[id]["fbref"]
        id = index["id"]
        name = index["name"].replace(" ", "-")

        if season:
            path = "/comps" + f"/{id}/{season}/{season}-{name}-Stats"
        else:
            path = "/comps" + f"/{id}/{name}-Stats"

        response = await self.get(path)
        return response

    async def get_team(
        self,
        id: str,
        name: str,
        season: str | None = None,
    ) -> httpx.Response:
        if season:
            path = "/squads" + f"/{id}/{season}/{name}-Stats"
        else:
            path = "/squads" + f"/{id}/{name}-Stats"

        response = await self.get(path)
        return response

    async def get_player(self, id: str, name: str) -> httpx.Response:
        path = f"/players/{id}/{name}"
        response = await self.get(path)
        return response

    async def get_matches(self, date: str) -> httpx.Response:
        path = f"/matches/{date}"
        response = await self.get(path)
        return response

    async def get_match(self, id: str) -> httpx.Response:
        path = f"/matches/{id}"
        response = await self.get(path)
        return response
