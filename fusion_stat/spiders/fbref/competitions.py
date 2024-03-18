import httpx
from parsel import Selector
from rapidfuzz import process

from ...config import CompetitionsConfig
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL


class Item(BaseItem):
    path_name: str
    country_code: str


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=f"{BASE_URL}/comps/")

    def parse(self, response: httpx.Response) -> list[Item]:
        selector = Selector(response.text)

        choices: list[tuple[str, str, str, str]] = []
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            # 在没有国家代码的赛事统一采用 fotmob 的规则，命名为 INT
            country_code = (
                tr.xpath('./td[@data-stat="country"]/a[2]/text()').get()
                or "INT"
            )
            if country_code in CompetitionsConfig.countries:
                id_ = href_strs[3]
                path_name_strs = href_strs[-1].split("-")[:-1]
                path_name = "-".join(path_name_strs)
                name = " ".join(path_name_strs)
                choices.append((country_code, name, id_, path_name))

        competitions: list[Item] = []
        for query in CompetitionsConfig.data:
            result = process.extractOne(
                query,
                choices,
                processor=lambda x: x[1],
            )[0]
            competitions.append(
                Item(
                    id=result[2],
                    name=query[1],
                    country_code=result[0],
                    path_name=result[3],
                )
            )

        return competitions
