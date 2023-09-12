import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel

from .base import JSONClient


class Competition(BaseModel):
    content: typing.Any
    name: str


class Team(BaseModel):
    content: typing.Any
    name: str


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

    async def get_match(self, code: str) -> MatchDetails:
        path = "/matchDetails"
        params = {"matchId": code}
        json = await self.get(path, params=params)
        return self._parse_match(json)

    def _parse_competition(self, content: typing.Any) -> Competition:
        name = content["details"]["name"]
        return Competition(content=content, name=name)

    def _parse_team(self, content: typing.Any) -> Team:
        name = content["details"]["name"]
        return Team(content=content, name=name)

    def _parse_player(self, content: typing.Any) -> Player:
        name = content["name"]
        return Player(content=content, name=name)

    def _parse_matches(self, content: typing.Any) -> Matches:
        date = content["date"]
        return Matches(content=content, date=date)

    def _parse_match(self, content: typing.Any) -> MatchDetails:
        home_team = content["general"]["homeTeam"]["name"]
        away_team = content["general"]["awayTeam"]["name"]
        return MatchDetails(
            content=content,
            home_team=home_team,
            away_team=away_team,
        )
