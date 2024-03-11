import httpx
from parsel import Selector

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, HEADERS


class Item(BaseItem):
    path_name: str


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET", url=f"{BASE_URL}/wettbewerbe/europa", headers=HEADERS
        )

    def parse(self, response: httpx.Response) -> list[Item]:
        competitions: list[Item] = []

        selector = Selector(response.text)
        competitions_id = {
            params["transfermarkt_id"] for params in COMPETITIONS.values()
        }
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs[1:]:
            a = tr.xpath("./td[1]/table/tr/td[2]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            id_ = href_strs[-1]
            if id_ in competitions_id:
                name = get_element_text(a.xpath("./text()"))
                path_name = href_strs[-4]
                competitions.append(
                    Item(
                        id=id_,
                        name=name,
                        path_name=path_name,
                    )
                )
        return competitions
