import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, ShootingItem, parse_shooting


class Item(BaseItem):
    shooting: ShootingItem


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name

    @property
    def request(self) -> httpx.Request:
        path = f"/players/{self.id}/"
        if self.path_name:
            path = f"{path}{self.path_name}"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/span/text()"))

        tr = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]/tfoot/tr[1]'
        )
        try:
            shooting = parse_shooting(tr)
        except ValueError:
            shooting = ShootingItem(shots=0, xg=0)

        return Item(id=self.id, name=name, shooting=shooting)
