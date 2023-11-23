# competition historic api 没有当前赛季
# 而且在 22 赛季以前使用的 id 与之后是不一样的

import httpx
from parsel import Selector

from fusion_stat.base import Spider
from fusion_stat.models import (
    CompetitionOfficial,
    CompetitionOfficialTeam,
)
from fusion_stat.utils import current_season, get_element_text

BASE_URL = "https://www.bundesliga.com"


class Competition(Spider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.name = name
        _current_season = current_season()
        if season:
            self.is_current_season = season == _current_season[0]
            self.season = f"{season}-{season + 1}"
        else:
            self.is_current_season = True
            self.season = f"{_current_season[0]}-{_current_season[1]}"

    @property
    def request(self) -> httpx.Request:
        if self.is_current_season:
            path = "/en/bundesliga/clubs"
        else:
            path = f"/assets/historic-season/{self.season}.json"
        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> CompetitionOfficial:
        if self.is_current_season:
            teams = self._parse_current_season_teams(response)
        else:
            teams = self._parse_historic_season_teams(response)
        return CompetitionOfficial(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=BASE_URL + "/assets/favicons/safari-pinned-tab_new.svg",
            teams=teams,
        )

    def _parse_current_season_teams(
        self, response: httpx.Response
    ) -> tuple[CompetitionOfficialTeam, ...]:
        selector = Selector(response.text)
        club_cards = selector.xpath('//div[@class="clubs grid"]/club-card')
        teams = []
        for card in club_cards:
            id = get_element_text(card.xpath("./a/@href")).split("/")[-1]

            img = card.xpath(".//img")
            name = get_element_text(img.xpath("./@alt"))
            logo = BASE_URL + get_element_text(img.xpath("./@src"))

            teams.append(CompetitionOfficialTeam(id=id, name=name, logo=logo))
        return tuple(teams)

    def _parse_historic_season_teams(
        self, response: httpx.Response
    ) -> tuple[CompetitionOfficialTeam, ...]:
        json = response.json()
        teams = []
        for team in json["entries"]:
            club = team["club"]

            id = club["slugifiedFull"]
            name = club["nameFull"]

            club_id = club["id"]
            if club["logoUrl"]:
                logo = f"{BASE_URL}/assets/clublogo/{club_id}.svg"
            else:
                logo = ""

            teams.append(CompetitionOfficialTeam(id=id, name=name, logo=logo))
        return tuple(teams)
