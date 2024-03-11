import typing

import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL, parse_score


class TeamItem(BaseItem):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class MatchTeamItem(BaseItem):
    score: int | None


class MatchItem(BaseItem):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    competition: BaseItem
    home: MatchTeamItem
    away: MatchTeamItem


class Item(BaseItem):
    type: str
    season: str
    country_code: str
    names: set[str]
    teams: list[TeamItem]
    matches: list[MatchItem]


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        season: int | None = None,
    ) -> None:
        self.id = id
        if season is None:
            self.season = season
        else:
            self.season = f"{season}/{season + 1}"

    @property
    def request(self) -> httpx.Request:
        params = {"id": self.id}
        if self.season is not None:
            params["season"] = self.season
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/leagues",
            params=params,
        )

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        name = json["details"]["name"]
        type_ = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        country_code = json["details"]["country"]
        names = {name, json["details"]["shortName"]}

        teams = [
            self._parse_team(node)
            for node in json["table"][0]["data"]["table"]["all"]
        ]

        matches = [
            self._parse_match(node, name)
            for node in json["matches"]["allMatches"]
        ]

        return Item(
            id=self.id,
            name=name,
            type=type_,
            season=season,
            country_code=country_code,
            names=names,
            teams=teams,
            matches=matches,
        )

    def _parse_team(self, node: typing.Any) -> TeamItem:
        goals_for, goals_against = node["scoresStr"].split("-")
        return TeamItem(
            id=str(node["id"]),
            name=node["name"],
            names={node["name"], node["shortName"]},
            played=node["played"],
            wins=node["wins"],
            draws=node["draws"],
            losses=node["losses"],
            goals_for=int(goals_for),
            goals_against=int(goals_against),
            points=int(node["pts"]),
        )

    def _parse_match(
        self, node: typing.Any, competition_name: str
    ) -> MatchItem:
        home_name = node["home"]["name"]
        away_name = node["away"]["name"]
        home_score, away_score = parse_score(node["status"].get("scoreStr"))
        return MatchItem(
            id=str(node["id"]),
            name=f"{home_name} vs {away_name}",
            utc_time=node["status"]["utcTime"],
            finished=node["status"]["finished"],
            started=node["status"]["started"],
            cancelled=node["status"]["cancelled"],
            competition=BaseItem(id=self.id, name=competition_name),
            home=MatchTeamItem(
                id=str(node["home"]["id"]),
                name=home_name,
                score=home_score,
            ),
            away=MatchTeamItem(
                id=str(node["away"]["id"]),
                name=away_name,
                score=away_score,
            ),
        )
