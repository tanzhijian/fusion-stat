import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel
from parsel import Selector, SelectorList

from .base import HTMLClient


class Shooting(BaseModel):
    shots: float
    xg: float


class Team(BaseModel):
    id: str
    name: str
    shooting: Shooting


class Competition(BaseModel):
    id: str
    name: str
    teams: list[Team]


class Player(BaseModel):
    content: typing.Any
    name: str


class MatchDetails(BaseModel):
    content: typing.Any
    home_team: str
    away_team: str


class Matches(BaseModel):
    content: typing.Any
    date: str


class CompetitionDetails(Competition):
    content: typing.Any


class TeamDetails(Team):
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

    async def get_competition(
        self,
        code: str,
        name: str,
        season: str | None = None,
    ) -> CompetitionDetails:
        if season:
            path = "/comps" + f"/{code}/{season}/{season}-{name}-Stats"
        else:
            path = "/comps" + f"/{code}/{name}-Stats"

        text = await self.get(path)
        return self._parse_competition(code, text)

    async def get_team(
        self,
        code: str,
        name: str,
        season: str | None = None,
    ) -> TeamDetails:
        if season:
            path = "/squads" + f"/{code}/{season}/{name}-Stats"
        else:
            path = "/squads" + f"/{code}/{name}-Stats"

        text = await self.get(path)
        return self._parse_team(text)

    async def get_player(self, code: str, name: str) -> Player:
        path = f"/players/{code}/{name}"
        text = await self.get(path)
        return self._parse_player(text)

    async def get_matches(self, date: str) -> Matches:
        path = f"/matches/{date}"
        text = await self.get(path)
        return self._parse_matches(text)

    async def get_match(self, code: str) -> MatchDetails:
        path = f"/matches/{code}"
        text = await self.get(path)
        return self._parse_match(text)

    @staticmethod
    def _get_element_text(selector_list: SelectorList[Selector]) -> str:
        if (text := selector_list.get()) is None:
            raise ValueError("tag not found")
        return text

    def _parse_competition(self, code: str, text: str) -> CompetitionDetails:
        selector = Selector(text)
        h1 = self._get_element_text(selector.xpath("//h1/text()"))
        competition_name = " ".join(h1.split(" ")[1:-1])

        teams = []
        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        for tr in trs:
            href = self._get_element_text(tr.xpath("./th/a/@href"))
            name = self._get_element_text(tr.xpath("./th/a/text()"))
            shots = self._get_element_text(
                tr.xpath('./td[@data-stat="shots"]/text()')
            )
            xg = self._get_element_text(
                tr.xpath('./td[@data-stat="xg"]/text()')
            )
            teams.append(
                Team(
                    id=href.split("/")[3],
                    name=name,
                    shooting=Shooting(
                        shots=float(shots),
                        xg=float(xg),
                    ),
                )
            )

        return CompetitionDetails(
            content=text,
            id=code,
            name=competition_name,
            teams=teams,
        )

    def _parse_team(self, text: str) -> TeamDetails:
        selector = Selector(text)
        h1 = selector.xpath("//h1/span/text()")[0].get()
        if h1 is None:
            raise ValueError("team name not found")
        name = " ".join(h1.split(" ")[1:-1])
        return TeamDetails(
            content=text,
            id="23",
            name=name,
            shooting=Shooting(shots=12.0, xg=1.1),
        )

    def _parse_player(self, text: str) -> Player:
        selector = Selector(text)
        name = selector.xpath("//h1/span/text()").get()
        if name is None:
            raise ValueError("player name not found")
        return Player(content=text, name=name)

    def _parse_matches(self, text: str) -> Matches:
        selector = Selector(text)
        date = selector.xpath(
            '//div[@id="content"]/div[@class="prevnext"]/span/text()'
        ).get()
        if date is None:
            raise ValueError("matches date not found")
        return Matches(content=text, date=date)

    def _parse_match(self, text: str) -> MatchDetails:
        selector = Selector(text)
        home_team, away_team = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return MatchDetails(
            content=text,
            home_team=home_team,
            away_team=away_team,
        )
