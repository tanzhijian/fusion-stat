import typing

import httpx

from .base import Downloader
from fusion_stat.utils import current_season


class Wikipedia(Downloader):
    def __init__(
        self, client: httpx.AsyncClient, **kwargs: typing.Any
    ) -> None:
        super().__init__(client, **kwargs)
        self.base_url = "https://en.wikipedia.org/wiki"

    async def get_competition(self, id: str) -> httpx.Response:
        start, end = current_season()
        path = f"/{start}-{str(end)[2:]}_{id}"
        url = self.base_url + path
        response = await self.get(url)
        return response
