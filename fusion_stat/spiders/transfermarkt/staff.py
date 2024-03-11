import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, HEADERS


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str,
    ) -> None:
        self.id = id
        self.path_name = path_name

    @property
    def request(self) -> httpx.Request:
        path = f"/{self.path_name}/profil/trainer/{self.id}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}", headers=HEADERS)

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        name = get_element_text(
            selector.xpath(
                '//div[@class="data-header__profile-container"]//img/@title'
            )
        )
        return Item(id=self.id, name=name)
