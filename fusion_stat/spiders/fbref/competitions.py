import httpx
from parsel import Selector

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from . import BASE_URL


class Item(BaseItem):
    path_name: str
    country_code: str


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=f"{BASE_URL}/comps/")

    def parse(self, response: httpx.Response) -> list[Item]:
        competitions: list[Item] = []

        selector = Selector(response.text)
        competitions_id = {
            params["fbref_id"] for params in COMPETITIONS.values()
        }
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            id_ = href_strs[3]
            if id_ in competitions_id:
                # 在没有国家代码的赛事统一采用 fotmob 的规则，命名为 INT
                country_code = (
                    tr.xpath('./td[@data-stat="country"]/a[2]/text()').get()
                    or "INT"
                )
                path_name_strs = href_strs[-1].split("-")[:-1]
                path_name = "-".join(path_name_strs)
                name = " ".join(path_name_strs)
                competitions.append(
                    Item(
                        id=id_,
                        name=name,
                        path_name=path_name,
                        country_code=country_code,
                    )
                )
        return competitions
