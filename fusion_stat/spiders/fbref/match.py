import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.id}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        home_name, away_name = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return Item(
            id=self.id,
            name=f"{home_name} vs {away_name}",
        )
