import httpx
from parsel import Selector

from ..base import Spider
from ..types import competition_types
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


class Competition(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name
        self.season = season

    @property
    def request(self) -> httpx.Request:
        params = {}
        path = f"/{self.path_name}/startseite/wettbewerb/{self.id}"
        if self.season:
            path = f"{path}/plus/"
            params["saison_id"] = self.season
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}{path}",
            params=params,
        )

    def parse(
        self, response: httpx.Response
    ) -> competition_types.TransfermarktDict:
        selector = Selector(response.text)

        teams: list[competition_types.TransfermarktTeamDict] = []
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs:
            a = tr.xpath("./td[7]/a")
            href = get_element_text(a.xpath("./@href"))
            id_ = href.split("/")[-3]
            name = get_element_text(a.xpath("./@title"))
            total_market_value = get_element_text(a.xpath("./text()"))
            team = competition_types.TransfermarktTeamDict(
                id=id_,
                name=name,
                total_market_value=total_market_value,
            )
            teams.append(team)

        return competition_types.TransfermarktDict(
            id=self.id,
            name=self.path_name.replace("-", " ").title(),
            teams=teams,
        )
