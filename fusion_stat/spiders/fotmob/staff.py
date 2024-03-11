import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/playerData",
            params={"id": self.id},
        )

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        name = json["name"]
        return Item(id=self.id, name=name)
