import typing

import httpx

from ...scraper import BaseItem, BaseSpider
from . import BASE_URL, parse_score


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
            self._parse_team(team)
            for team in json["table"][0]["data"]["table"]["all"]
        ]

        matches = [
            self._parse_match(match, name)
            for match in json["matches"]["allMatches"]
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

    def _parse_team(self, team: typing.Any) -> TeamItem:
        goals_for, goals_against = team["scoresStr"].split("-")
        return TeamItem(
            id=str(team["id"]),
            name=team["name"],
            names={team["name"], team["shortName"]},
            played=team["played"],
            wins=team["wins"],
            draws=team["draws"],
            losses=team["losses"],
            goals_for=int(goals_for),
            goals_against=int(goals_against),
            points=int(team["pts"]),
        )

    def _parse_match(
        self, match: typing.Any, competition_name: str
    ) -> MatchItem:
        home_name = match["home"]["name"]
        away_name = match["away"]["name"]
        home_score, away_score = parse_score(match["status"].get("scoreStr"))
        return MatchItem(
            id=str(match["id"]),
            name=f"{home_name} vs {away_name}",
            utc_time=match["status"]["utcTime"],
            finished=match["status"]["finished"],
            started=match["status"]["started"],
            cancelled=match["status"]["cancelled"],
            competition=BaseItem(id=self.id, name=competition_name),
            home=MatchTeamItem(
                id=str(match["home"]["id"]),
                name=home_name,
                score=home_score,
            ),
            away=MatchTeamItem(
                id=str(match["away"]["id"]),
                name=away_name,
                score=away_score,
            ),
        )
