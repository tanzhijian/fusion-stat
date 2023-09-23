import httpx
from httpx._types import ProxiesTypes

from .base import Client
from fusion_stat.config import COMPETITIONS_INDEX


class FotMob(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(
            client_cls,
            base_url="https://www.fotmob.com/api",
            proxies=proxies,
        )

    async def get_competitions(self) -> httpx.Response:
        path = "/allLeagues"
        response = await self.get(path)
        return response

    async def get_competition(self, id: str) -> httpx.Response:
        path = "/leagues"
        id = COMPETITIONS_INDEX[id]["fotmob"]["id"]
        params = {"id": id}
        response = await self.get(path, params=params)
        return response

    async def get_team(self, id: str) -> httpx.Response:
        path = "/teams"
        params = {"id": id}
        response = await self.get(path, params=params)
        return response

    async def get_player(self, id: str) -> httpx.Response:
        path = "/playerData"
        params = {"id": id}
        response = await self.get(path, params=params)
        return response

    async def get_matches(self, date: str | None = None) -> httpx.Response:
        path = "/matches"
        params = {"date": date}
        response = await self.get(path, params=params)
        return response

    async def get_match(self, id: str) -> httpx.Response:
        path = "/matchDetails"
        params = {"matchId": id}
        response = await self.get(path, params=params)
        return response
