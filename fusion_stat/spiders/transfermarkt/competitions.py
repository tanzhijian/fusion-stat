import httpx
from parsel import Selector
from rapidfuzz import process

from ...config import CompetitionsConfig, fifa_members
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, HEADERS


class Item(BaseItem):
    country_code: str
    path_name: str


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET", url=f"{BASE_URL}/wettbewerbe/europa", headers=HEADERS
        )

    def parse(self, response: httpx.Response) -> list[Item]:
        selector = Selector(response.text)

        choices: list[tuple[str, str, str, str]] = []
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs[1:]:
            country = get_element_text(tr.xpath("./td[2]/img/@title"))
            country_code = fifa_members[country].code

            if country_code in CompetitionsConfig.countries:
                a = tr.xpath("./td[1]/table/tr/td[2]/a")
                href_strs = get_element_text(a.xpath("./@href")).split("/")
                id_ = href_strs[-1]
                name = get_element_text(a.xpath("./text()"))
                path_name = href_strs[-4]
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
