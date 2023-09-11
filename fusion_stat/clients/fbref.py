import httpx
from httpx._types import ProxiesTypes

from .base import HTMLClient


class FBref(HTMLClient):
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

    async def get_competition(
        self,
        code: str,
        name: str,
        season: str | None = None,
    ) -> str:
        if season:
            path = "/comps" + f"/{code}/{season}/{season}-{name}-Stats"
        else:
            path = "/comps" + f"/{code}/{name}-Stats"

        text = await self.get(path)
        return text

    async def get_team(
        self,
        code: str,
        name: str,
        season: str | None = None,
    ) -> str:
        if season:
            path = "/squads" + f"/{code}/{season}/{name}-Stats"
        else:
            path = "/squads" + f"/{code}/{name}-Stats"

        text = await self.get(path)
        return text

    async def get_player(self, code: str, name: str) -> str:
        path = f"/players/{code}/{name}"
        text = await self.get(path)
        return text

    async def get_matches(self, date: str) -> str:
        path = f"/matches/{date}"
        text = await self.get(path)
        return text

    async def get_match(self, code: str) -> str:
        path = f"/matches/{code}"
        text = await self.get(path)
        return text
