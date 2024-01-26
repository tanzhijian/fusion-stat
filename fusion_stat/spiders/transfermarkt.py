from datetime import datetime

import httpx
from parsel import Selector

from ..config import COMPETITIONS, POSITIONS, fifa_members
from ..scraper import Spider
from ..types import (
    competition_types,
    competitions_types,
    player_types,
    staff_types,
    team_types,
)
from ..utils import get_element_text

BASE_URL = "https://www.transfermarkt.com"
HEADERS = {"User-Agent": "firefox"}


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET", url=f"{BASE_URL}/wettbewerbe/europa", headers=HEADERS
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
    ) -> None:
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
            "GET", url=f"{BASE_URL}{path}", params=params, headers=HEADERS
        )

    def parse(
        self, response: httpx.Response
    ) -> competition_types.TransfermarktDict:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/text()"))
        player_average_market_value = get_element_text(
            selector.xpath(
                '//div[@class="data-header__details"]/ul[2]/li[1]/span/text()'
            )
        )
        market_values = _get_market_value(selector)

        teams: list[competition_types.TransfermarktTeamDict] = []
        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in trs:
            a = tr.xpath("./td[7]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            team_id = href_strs[-3]
            team_path_name = href_strs[-6]
            team_name = get_element_text(a.xpath("./@title"))
            team_market_values = get_element_text(a.xpath("./text()"))
            team = competition_types.TransfermarktTeamDict(
                id=team_id,
                name=team_name,
                market_values=team_market_values,
                path_name=team_path_name,
            )
            teams.append(team)

        return competition_types.TransfermarktDict(
            id=self.id,
            name=name,
            market_values=market_values,
            player_average_market_value=player_average_market_value,
            teams=teams,
        )


class Team(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str,
        season: int | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name
        self.season = season

    @property
    def request(self) -> httpx.Request:
        path = f"/{self.path_name}/startseite/verein/{self.id}"
        if self.season is not None:
            path = f"{path}/saison_id/{self.season}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}", headers=HEADERS)

    def parse(self, response: httpx.Response) -> team_types.TransfermarktDict:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/text()"))
        market_values = _get_market_value(selector)

        players: list[team_types.TransfermarktPlayerDict] = []
        player_trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        for tr in player_trs:
            tds = tr.xpath("./td")

            a = tds[1].xpath("./table/tr[1]/td[2]/a")
            href_strs = get_element_text(a.xpath("./@href")).split("/")
            player_id = href_strs[-1]
            player_path_name = href_strs[-4]
            player_name = get_element_text(a.xpath("./text()"))

            position = get_element_text(tds[1].xpath("./table/tr[2]/td/text()"))
            position = POSITIONS[position]

            date_of_birth = get_element_text(tds[2].xpath("./text()"))
            date_of_birth = _convert_date_format(date_of_birth)

            player_market_values = get_element_text(tds[-1].xpath("./a/text()"))

            country = get_element_text(tds[-2].xpath("./img[1]/@title"))
            country_code = fifa_members[(country)].code

            players.append(
                team_types.TransfermarktPlayerDict(
                    id=player_id,
                    name=player_name,
                    date_of_birth=date_of_birth,
                    market_values=player_market_values,
                    path_name=player_path_name,
                    country_code=country_code,
                    position=position,
                )
            )

        return team_types.TransfermarktDict(
            id=self.id,
            name=name,
            market_values=market_values,
            players=players,
        )


class Player(Spider):
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
        path = f"/{self.path_name}/profil/spieler/{self.id}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}", headers=HEADERS)

    def parse(self, response: httpx.Response) -> player_types.TransfermarktDict:
        selector = Selector(response.text)
        market_values = _get_market_value(selector)

        name = get_element_text(
            selector.xpath(
                '//div[@class="data-header__profile-container"]//img/@title'
            )
        )
        return player_types.TransfermarktDict(
            id=self.id, name=name, market_values=market_values
        )


class Staff(Spider):
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

    def parse(self, response: httpx.Response) -> staff_types.TransfermarktDict:
        selector = Selector(response.text)
        name = get_element_text(
            selector.xpath(
                '//div[@class="data-header__profile-container"]//img/@title'
            )
        )
        return staff_types.TransfermarktDict(id=self.id, name=name)


def _convert_date_format(s: str) -> str:
    """
    'Aug 17, 1993 (30)' => '1993-08-17'
    """
    date_string = s.split(" (")[0]
    date_object = datetime.strptime(date_string, "%b %d, %Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date


def _get_market_value(selector: Selector) -> str:
    a = selector.xpath('//a[@class="data-header__market-value-wrapper"]')
    currency = get_element_text(a.xpath("./span[1]/text()"))
    number = get_element_text(a.xpath("./text()"))
    scale = get_element_text(a.xpath("./span[2]/text()"))
    market_values = f"{currency}{number}{scale}"
    return market_values
