import typing

import httpx

from fusion_stat.base import Spider
from fusion_stat.utils import current_season

BASE_URL = "https://en.wikipedia.org/api/rest_v1/page"


class Image(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        path = f"/summary/{self.id}"
        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> str:
        json = response.json()
        image_url: str = json["originalimage"]["source"]
        return image_url


class Competition(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        start, end = current_season()
        path = f"/mobile-html/{start}-{str(end)[2:]}_{self.id}"

        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> typing.Any:
        return "competition"
