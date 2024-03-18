import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str) -> None:
        self.date = date

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.date}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> list[Item]:
        # 填充
        return [Item(id="bdbc722e", name="Liverpool vs Aston Villa")]
