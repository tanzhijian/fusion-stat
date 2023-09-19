import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel

from .base import JSONClient
from fusion_stat.config import COMPETITIONS
from fusion_stat.utils import is_in


class Competition(BaseModel):
    id: str
    name: str


class Team(BaseModel):
    id: str
    name: str
    names: set[str]


class Player(BaseModel):
    id: str
    name: str
    country: str
    is_staff: bool


class Match(BaseModel):
    id: str
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Competition
    home: Team
    away: Team


class CompetitionDetails(Competition):
    content: typing.Any
    type: str
    season: str
    names: set[str]
    teams: list[Team]
    matches: list[Match]


class TeamDetails(Team):
    content: typing.Any
    players: list[Player]


class PlayerDetails(Player):
    content: typing.Any
    position: str


class MatchDetails(Match):
    content: typing.Any


class Matches(BaseModel):
    content: typing.Any
    date: str
    matches: list[Match]


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

    async def get_competitions(self) -> list[Competition]:
        path = "/allLeagues"
        json = await self.get(path)
        return self._parse_competitions(json)

    async def get_competition(self, id: str) -> CompetitionDetails:
        path = "/leagues"
        params = {"id": id}
        json = await self.get(path, params=params)
        return self._parse_competition(json)

    async def get_team(self, id: str) -> TeamDetails:
        path = "/teams"
        params = {"id": id}
        json = await self.get(path, params=params)
        return self._parse_team(json)

    async def get_player(self, id: str) -> PlayerDetails:
        path = "/playerData"
        params = {"id": id}
        json = await self.get(path, params=params)
        return self._parse_player(json)

    async def get_matches(self, date: str | None = None) -> Matches:
        path = "/matches"
        params = {"date": date}
        json = await self.get(path, params=params)
        return self._parse_matches(json)

    async def get_match(self, id: str) -> MatchDetails:
        path = "/matchDetails"
        params = {"matchId": id}
        json = await self.get(path, params=params)
        return self._parse_match(json)

    def _parse_competitions(self, json: typing.Any) -> list[Competition]:
        competitions = []
        selection = json["popular"]
        for competition in selection:
            if is_in(competition["name"], COMPETITIONS):
                competitions.append(
                    Competition(
                        id=str(competition["id"]),
                        name=competition["name"],
                    )
                )
        return competitions

    def _parse_competition(self, json: typing.Any) -> CompetitionDetails:
        id = str(json["details"]["id"])
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}

        teams = [
            Team(
                id=str(team["id"]),
                name=team["name"],
                names={team["name"], team["shortName"]},
            )
            for team in json["table"][0]["data"]["table"]["all"]
        ]

        matches = [
            Match(
                id=str(match["id"]),
                utc_time=match["status"]["utcTime"],
                finished=match["status"]["finished"],
                started=match["status"]["started"],
                cancelled=match["status"]["cancelled"],
                score=match["status"].get("scoreStr"),
                competition=Competition(id=id, name=name),
                home=Team(
                    id=str(match["home"]["id"]),
                    name=match["home"]["name"],
                    names={match["home"]["name"], match["home"]["shortName"]},
                ),
                away=Team(
                    id=str(match["away"]["id"]),
                    name=match["away"]["name"],
                    names={match["away"]["name"], match["away"]["shortName"]},
                ),
            )
            for match in json["matches"]["allMatches"]
        ]

        return CompetitionDetails(
            content=json,
            id=id,
            type=type,
            season=season,
            name=name,
            names=names,
            teams=teams,
            matches=matches,
        )

    def _parse_team(self, json: typing.Any) -> TeamDetails:
        id = str(json["details"]["id"])
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}

        players = []
        for role in json["squad"]:
            for player in role[1:]:
                players.append(
                    Player(
                        id=str(player[0]["id"]),
                        name=player[0]["name"],
                        country=player[0]["cname"],
                        is_staff=player[0].get("role") is None,
                    )
                )

        return TeamDetails(
            content=json,
            id=id,
            name=name,
            names=names,
            players=players,
        )

    def _parse_player(self, json: typing.Any) -> PlayerDetails:
        id = str(json["id"])
        name = json["name"]
        country = json["meta"]["personJSONLD"]["nationality"]["name"]
        position = json["origin"]["positionDesc"]["primaryPosition"]["label"]
        is_staff = position == "Coach"
        return PlayerDetails(
            content=json,
            id=id,
            name=name,
            country=country,
            is_staff=is_staff,
            position=position,
        )

    def _parse_matches(self, json: typing.Any) -> Matches:
        date = json["date"]

        matches = []
        for league in json["leagues"]:
            competition_id = str(league["id"])
            competition_name = league["name"]
            for match in league["matches"]:
                matches.append(
                    Match(
                        id=str(match["id"]),
                        utc_time=match["status"]["utcTime"],
                        finished=match["status"]["finished"],
                        started=match["status"]["started"],
                        cancelled=match["status"]["cancelled"],
                        score=match["status"].get("scoreStr"),
                        competition=Competition(
                            id=competition_id,
                            name=competition_name,
                        ),
                        home=Team(
                            id=str(match["home"]["id"]),
                            name=match["home"]["longName"],
                            names={
                                match["home"]["longName"],
                                match["home"]["name"],
                            },
                        ),
                        away=Team(
                            id=str(match["away"]["id"]),
                            name=match["away"]["longName"],
                            names={
                                match["away"]["longName"],
                                match["away"]["name"],
                            },
                        ),
                    )
                )

        return Matches(content=json, date=date, matches=matches)

    def _parse_match(self, json: typing.Any) -> MatchDetails:
        id = str(json["general"]["matchId"])
        utc_time = json["header"]["status"]["utcTime"]
        finished = json["header"]["status"]["finished"]
        started = json["header"]["status"]["started"]
        cancelled = json["header"]["status"]["cancelled"]
        score = json["header"]["status"].get("scoreStr")

        competition = Competition(
            id=str(json["general"]["leagueId"]),
            name=json["general"]["leagueName"],
        )

        home_team = json["header"]["teams"][0]
        home = Team(
            id=str(home_team["id"]),
            name=home_team["name"],
            names={home_team["name"]},
        )
        away_team = json["header"]["teams"][1]
        away = Team(
            id=str(away_team["id"]),
            name=away_team["name"],
            names={away_team["name"]},
        )

        return MatchDetails(
            content=json,
            id=id,
            utc_time=utc_time,
            finished=finished,
            started=started,
            cancelled=cancelled,
            score=score,
            competition=competition,
            home=home,
            away=away,
        )
