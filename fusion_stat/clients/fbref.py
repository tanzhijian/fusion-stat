import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel
from parsel import Selector, SelectorList
from rapidfuzz import process

from .base import HTMLClient
from fusion_stat.config import COMPETITIONS, SCORE_CUTOFF


class Shooting(BaseModel):
    shots: float
    xg: float


class Player(BaseModel):
    id: str
    name: str
    shooting: Shooting


class Team(BaseModel):
    id: str
    name: str
    shooting: Shooting


class Competition(BaseModel):
    id: str
    name: str


class MatchDetails(BaseModel):
    content: typing.Any
    home_team: str
    away_team: str


class Matches(BaseModel):
    content: typing.Any
    date: str


class CompetitionDetails(Competition):
    content: str
    teams: list[Team]


class TeamDetails(Team):
    content: typing.Any
    players: list[Player]


class PlayerDetails(Player):
    content: typing.Any


class FBref(HTMLClient):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(
            client_cls,
            base_url="https://fbref.com/en",
            proxies=proxies,
        )

    async def get_competitions(self) -> list[Competition]:
        path = "/comps/"
        selector = await self.get(path)
        return self._parse_competitions(selector)

    async def get_competition(
        self,
        id: str,
        name: str,
        season: str | None = None,
    ) -> CompetitionDetails:
        if season:
            path = "/comps" + f"/{id}/{season}/{season}-{name}-Stats"
        else:
            path = "/comps" + f"/{id}/{name}-Stats"

        selector = await self.get(path)
        return self._parse_competition(id, selector)

    async def get_team(
        self,
        id: str,
        name: str,
        season: str | None = None,
    ) -> TeamDetails:
        if season:
            path = "/squads" + f"/{id}/{season}/{name}-Stats"
        else:
            path = "/squads" + f"/{id}/{name}-Stats"

        selector = await self.get(path)
        return self._parse_team(id, selector)

    async def get_player(self, id: str, name: str) -> Player:
        path = f"/players/{id}/{name}"
        selector = await self.get(path)
        return self._parse_player(id, selector)

    async def get_matches(self, date: str) -> Matches:
        path = f"/matches/{date}"
        selector = await self.get(path)
        return self._parse_matches(selector)

    async def get_match(self, id: str) -> MatchDetails:
        path = f"/matches/{id}"
        selector = await self.get(path)
        return self._parse_match(selector)

    def _parse_shooting(
        self, tr: Selector | SelectorList[Selector]
    ) -> Shooting:
        shots = self._get_element_text(
            tr.xpath('./td[@data-stat="shots"]/text()')
        )
        xg = self._get_element_text(tr.xpath('./td[@data-stat="xg"]/text()'))
        return Shooting(
            shots=float(shots),
            xg=float(xg),
        )

    def _parse_competitions(self, selector: Selector) -> list[Competition]:
        competitions = []
        index = set()
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href = self._get_element_text(tr.xpath("./th/a/@href")).split("/")
            id = href[3]
            if id not in index:
                index.add(id)
                gender = self._get_element_text(
                    tr.xpath("./td[@data-stat='gender']/text()")
                )
                name = " ".join(href[-1].split("-")[:-1])
                if (
                    process.extractOne(
                        name, COMPETITIONS, score_cutoff=SCORE_CUTOFF
                    )
                    and gender == "M"
                ):
                    competitions.append(
                        Competition(
                            id=id,
                            name=name,
                        )
                    )
        return competitions

    def _parse_competition(
        self,
        id: str,
        selector: Selector,
    ) -> CompetitionDetails:
        h1 = self._get_element_text(selector.xpath("//h1/text()"))
        competition_name = " ".join(h1.split(" ")[1:-1])

        teams = []
        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        for tr in trs:
            href = self._get_element_text(tr.xpath("./th/a/@href"))
            name = self._get_element_text(tr.xpath("./th/a/text()"))
            shooting = self._parse_shooting(tr)
            teams.append(
                Team(
                    id=href.split("/")[3],
                    name=name,
                    shooting=shooting,
                )
            )

        return CompetitionDetails(
            content=selector.get(),
            id=id,
            name=competition_name,
            teams=teams,
        )

    def _parse_team(self, id: str, selector: Selector) -> TeamDetails:
        h1 = self._get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])

        table = selector.xpath('//table[starts-with(@id,"stats_shooting_")]')

        team_shooting = self._parse_shooting(table.xpath("./tfoot/tr[1]"))

        players = []
        trs = table.xpath("./tbody/tr")
        for tr in trs:
            href = self._get_element_text(tr.xpath("./th/a/@href"))
            name = self._get_element_text(tr.xpath("./th/a/text()"))
            shooting = self._parse_shooting(tr)
            players.append(
                Player(
                    id=href.split("/")[3],
                    name=name,
                    shooting=shooting,
                )
            )

        return TeamDetails(
            content=selector.get(),
            id=id,
            name=team_name,
            shooting=team_shooting,
            players=players,
        )

    def _parse_player(self, id: str, selector: Selector) -> Player:
        name = self._get_element_text(selector.xpath("//h1/span/text()"))

        tr = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]/tfoot/tr[1]'
        )
        shooting = self._parse_shooting(tr)

        return PlayerDetails(
            content=selector.get(),
            id=id,
            name=name,
            shooting=shooting,
        )

    def _parse_matches(self, selector: Selector) -> Matches:
        date = selector.xpath(
            '//div[@id="content"]/div[@class="prevnext"]/span/text()'
        ).get()
        if date is None:
            raise ValueError("matches date not found")
        return Matches(content=selector.get(), date=date)

    def _parse_match(self, selector: Selector) -> MatchDetails:
        home_team, away_team = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return MatchDetails(
            content=selector.get(),
            home_team=home_team,
            away_team=away_team,
        )
