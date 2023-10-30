import typing

import httpx

from fusion_stat.base import Spider
from fusion_stat.utils import current_season


BASE_URL = "https://en.wikipedia.org/wiki"


class Competition(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    module_name = "wikipedia"

    @property
    def request(self) -> httpx.Request:
        start, end = current_season()
        path = f"/{start}-{str(end)[2:]}_{self.id}"

        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> typing.Any:
        return "competition"
