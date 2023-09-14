import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel

from .base import JSONClient


class TeamSlim(BaseModel):
    id: str
    name: str
    names: set[str]


class MatchSlim(BaseModel):
    id: str
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    home: TeamSlim
    away: TeamSlim


class Competition(BaseModel):
    content: typing.Any
    id: str
    type: str
    season: str
    name: str
    names: set[str]
    teams: list[TeamSlim]
    matches: list[MatchSlim]


class Team(BaseModel):
    content: typing.Any
    name: str


class Player(BaseModel):
    content: typing.Any
    name: str


class Match(BaseModel):
    content: typing.Any
    home_team: str
    away_team: str


class Matches(BaseModel):
    content: typing.Any
    date: str


class FotMob(JSONClient):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(
            client_cls,
            base_url="https://www.fotmob.com/api",
            proxies=proxies,
        )

    async def get_competition(self, code: str) -> Competition:
        path = "/leagues"
        params = {"id": code}
        json = await self.get(path, params=params)
        return self._parse_competition(json)

    async def get_team(self, code: str) -> Team:
        path = "/teams"
        params = {"id": code}
        json = await self.get(path, params=params)
        return self._parse_team(json)

    async def get_player(self, code: str) -> Player:
        path = "/playerData"
        params = {"id": code}
        json = await self.get(path, params=params)
        return self._parse_player(json)

    async def get_matches(self, date: str | None = None) -> Matches:
        path = "/matches"
        params = {"date": date}
        json = await self.get(path, params=params)
        return self._parse_matches(json)

    async def get_match(self, code: str) -> Match:
        path = "/matchDetails"
        params = {"matchId": code}
        json = await self.get(path, params=params)
        return self._parse_match(json)

    def _parse_competition(self, json: typing.Any) -> Competition:
        id = str(json["details"]["id"])
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}

        teams = [
            TeamSlim(
                id=str(team["id"]),
                name=team["name"],
                names={team["name"], team["shortName"]},
            )
            for team in json["table"][0]["data"]["table"]["all"]
        ]

        matches = [
            MatchSlim(
                id=str(match["id"]),
                utc_time=match["status"]["utcTime"],
                finished=match["status"]["finished"],
                started=match["status"]["started"],
                cancelled=match["status"]["cancelled"],
                score=match["status"].get("scoreStr"),
                home=TeamSlim(
                    id=str(match["home"]["id"]),
                    name=match["home"]["name"],
                    names={match["home"]["name"], match["home"]["shortName"]},
                ),
                away=TeamSlim(
                    id=str(match["away"]["id"]),
                    name=match["away"]["name"],
                    names={match["away"]["name"], match["away"]["shortName"]},
                ),
            )
            for match in json["matches"]["allMatches"]
        ]

        return Competition(
            content=json,
            id=id,
            type=type,
            season=season,
            name=name,
            names=names,
            teams=teams,
            matches=matches,
        )

    def _parse_team(self, json: typing.Any) -> Team:
        name = json["details"]["name"]
        return Team(content=json, name=name)

    def _parse_player(self, json: typing.Any) -> Player:
        name = json["name"]
        return Player(content=json, name=name)

    def _parse_matches(self, json: typing.Any) -> Matches:
        date = json["date"]
        return Matches(content=json, date=date)

    def _parse_match(self, json: typing.Any) -> Match:
        home_team = json["general"]["homeTeam"]["name"]
        away_team = json["general"]["awayTeam"]["name"]
        return Match(
            content=json,
            home_team=home_team,
            away_team=away_team,
        )
