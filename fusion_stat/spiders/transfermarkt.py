from datetime import datetime

import httpx
from parsel import Selector

from ..base import Spider
from ..config import COMPETITIONS, POSITIONS, fifa_members
from ..types import (
    competition_types,
    competitions_types,
    member_types,
    team_types,
)
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

    def parse(
        self, response: httpx.Response
    ) -> list[competitions_types.TransfermarktCompetitionDict]:
        competitions: list[competitions_types.TransfermarktCompetitionDict] = []

        selector = Selector(response.text)
        competitions_id = {
            params["transfermarkt_id"] for params in COMPETITIONS.values()
        }
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        # 还没有添加 config 的赛事限制
        for tr in trs[1:]:
            a = tr.xpath("./td[1]/table/tr/td[2]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            id_ = href_strs[-1]
            if id_ in competitions_id:
                name = get_element_text(a.xpath("./text()"))
                path_name = href_strs[-4]
                competitions.append(
                    competitions_types.TransfermarktCompetitionDict(
                        id=id_,
                        name=name,
                        path_name=path_name,
                    )
                )
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
        name = get_element_text(selector.xpath("//h1/text()")).strip()

        teams: list[competition_types.TransfermarktTeamDict] = []
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs:
            a = tr.xpath("./td[7]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            team_id = href_strs[-3]
            team_path_name = href_strs[-6]
            team_name = get_element_text(a.xpath("./@title"))
            total_market_value = get_element_text(a.xpath("./text()"))
            team = competition_types.TransfermarktTeamDict(
                id=team_id,
                name=team_name,
                total_market_value=total_market_value,
                path_name=team_path_name,
            )
            teams.append(team)

        return competition_types.TransfermarktDict(
            id=self.id,
            name=name,
            teams=teams,
        )


class Team(Spider):
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
        path = f"/{self.path_name}/startseite/verein/{self.id}"
        if self.season is not None:
            path = f"{path}/saison_id/{self.season}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> team_types.TransfermarktDict:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/text()")).strip()

        members: list[team_types.TransfermarktMemberDict] = []
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs:
            tds = tr.xpath("./td")

            a = tds[1].xpath("./table/tr[1]/td[2]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            member_id = href_strs[-1]
            member_path_name = href_strs[-4]
            member_name = get_element_text(a.xpath("./text()")).strip()

            position = get_element_text(
                tds[1].xpath("./table/tr[2]/td/text()")
            ).strip()
            position = POSITIONS[position]

            date_of_birth = get_element_text(tds[2].xpath("./text()"))
            date_of_birth = _convert_date_format(date_of_birth)

            market_values = get_element_text(tds[-1].xpath("./a/text()"))

            country = get_element_text(tds[-2].xpath("./img[1]/@title"))
            country_code = fifa_members[(country)].code

            members.append(
                team_types.TransfermarktMemberDict(
                    id=member_id,
                    name=member_name,
                    date_of_birth=date_of_birth,
                    market_values=market_values,
                    path_name=member_path_name,
                    country_code=country_code,
                    position=position,
                )
            )

        return team_types.TransfermarktDict(
            id=self.id,
            name=name,
            members=members,
        )


class Member(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name

    @property
    def request(self) -> httpx.Request:
        path = f"/{self.path_name}/profil/spieler/{self.id}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> member_types.TransfermarktDict:
        selector = Selector(response.text)

        a = selector.xpath('//a[@class="data-header__market-value-wrapper"]')
        currency = get_element_text(a.xpath("./span[1]/text()"))
        number = get_element_text(a.xpath("./text()"))
        scale = get_element_text(a.xpath("./span[2]/text()"))
        market_values = f"{currency}{number}{scale}"

        name = get_element_text(
            selector.xpath(
                '//div[@class="data-header__profile-container"]//img/@title'
            )
        )
        return member_types.TransfermarktDict(
            id=self.id, name=name, market_values=market_values
        )


def _convert_date_format(s: str) -> str:
    """
    'Aug 17, 1993 (30)' => '1993-08-17'
    """
    date_string = s.split(" (")[0]
    date_object = datetime.strptime(date_string, "%b %d, %Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date
