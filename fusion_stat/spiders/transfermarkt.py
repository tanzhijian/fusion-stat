import httpx
from parsel import Selector

from ..base import Spider
from ..types.base_types import StatDict
from ..utils import get_element_text

BASE_URL = "https://www.transfermarkt.com"
HEADERS = {"User-Agent": "googlebot"}


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/wettbewerbe/europa",
            headers=HEADERS,
        )

    def parse(self, response: httpx.Response) -> list[StatDict]:
        competitions: list[StatDict] = []

        selector = Selector(response.text)
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        # 还没有添加 config 的赛事限制
        for tr in trs[1:]:
            a = tr.xpath("./td[1]/table/tr/td[2]/a")
            name = get_element_text(a.xpath("./text()"))
            href = get_element_text(a.xpath("./@href"))
            id_ = href.split("/")[-1]

            competitions.append(StatDict(id=id_, name=name))
        return competitions
