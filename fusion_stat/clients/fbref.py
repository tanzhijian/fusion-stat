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
            path = f"/comps/{code}/{season}/{season}-{name}-Stats"
        else:
            path = f"/comps/{code}/{name}-Stats"

        text = await self.get(path)
        return text
