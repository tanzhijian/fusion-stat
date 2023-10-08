import typing

import httpx
from parsel import Selector
from pydantic import BaseModel
from rapidfuzz import process

from .base import FusionStat
from fusion_stat.utils import (
    get_element_text,
    parse_fbref_shooting,
    unpack_params,
    sort_table_key,
)
from .downloaders.base import Downloader
from .downloaders import FotMob, FBref
from .models import Stat, Params, FBrefShooting


class FotMobTeamModel(Stat):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class FotMobMatchModel(Stat):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Stat
    home: Stat
    away: Stat


class FBrefTeamModel(Stat):
    path_name: str
    names: set[str]
    shooting: FBrefShooting


class FotMobCompetitionModel(Stat):
    type: str
    season: str
    names: set[str]
    teams: tuple[FotMobTeamModel, ...]
    matches: tuple[FotMobMatchModel, ...]


class FBrefCompetitionModel(Stat):
    teams: tuple[FBrefTeamModel, ...]


class Response(BaseModel):
    fotmob: FotMobCompetitionModel
    fbref: FBrefCompetitionModel


class Competition(FusionStat[Response]):
    def __init__(
        self,
        params: Params | dict[str, str],
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client, **kwargs)
        self.params = unpack_params(params)

    @property
    def _downloaders_cls(self) -> list[type[Downloader]]:
        return [FotMob, FBref]

    async def _create_task(
        self, downloader_cls: type[Downloader], client: httpx.AsyncClient
    ) -> httpx.Response:
        downloader = downloader_cls(client=client, **self.kwargs)
        competition = await downloader.get_competition(self.params)
        return competition

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

    def _parse_fotmob(self, json: typing.Any) -> FotMobCompetitionModel:
        name = json["details"]["name"]
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        names = {name, json["details"]["shortName"]}

        teams = []
        for team in json["table"][0]["data"]["table"]["all"]:
            goals_for, goals_against = team["scoresStr"].split("-")
            teams.append(
                FotMobTeamModel(
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
            )

        matches = []
        for match in json["matches"]["allMatches"]:
            home_name = match["home"]["name"]
            away_name = match["away"]["name"]
            matches.append(
                FotMobMatchModel(
                    id=str(match["id"]),
                    name=f"{home_name} vs {away_name}",
                    utc_time=match["status"]["utcTime"],
                    finished=match["status"]["finished"],
                    started=match["status"]["started"],
                    cancelled=match["status"]["cancelled"],
                    score=match["status"].get("scoreStr"),
                    competition=Stat(id=self.params.fotmob_id, name=name),
                    home=Stat(
                        id=str(match["home"]["id"]),
                        name=home_name,
                    ),
                    away=Stat(
                        id=str(match["away"]["id"]),
                        name=away_name,
                    ),
                )
            )

        return FotMobCompetitionModel(
            id=self.params.fotmob_id,
            name=name,
            type=type,
            season=season,
            names=names,
            teams=tuple(teams),
            matches=tuple(matches),
        )

    def _parse_fbref(self, text: str) -> FBrefCompetitionModel:
        selector = Selector(text)
        h1 = get_element_text(selector.xpath("//h1/text()"))
        competition_name = " ".join(h1.split(" ")[1:-1])

        teams = []
        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        for tr in trs:
            href = get_element_text(tr.xpath("./th/a/@href")).split("/")
            name = " ".join(href[-1].split("-")[:-1])
            name_2 = get_element_text(tr.xpath("./th/a/text()"))
            shooting = parse_fbref_shooting(tr)
            teams.append(
                FBrefTeamModel(
                    id=href[3],
                    name=name_2,
                    path_name=name.replace(" ", "-"),
                    names={name, name_2},
                    shooting=shooting,
                )
            )
        return FBrefCompetitionModel(
            id=self.params.fbref_id,
            name=competition_name,
            teams=tuple(teams),
        )

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.response.fotmob.name,
            "type": self.response.fotmob.type,
            "season": self.response.fotmob.season,
            "names": self.response.fotmob.names | {self.response.fbref.name},
        }

    @property
    def teams(self) -> dict[str, dict[str, typing.Any]]:
        fotmob = self.response.fotmob.teams
        fbref = self.response.fbref.teams

        teams = {}
        for fotmob_team in fotmob:
            fbref_team = process.extractOne(
                fotmob_team, fbref, processor=lambda x: x.name
            )[0]

            team = fotmob_team.model_dump()
            team["names"] |= fbref_team.names
            team["shooting"] = fbref_team.shooting.model_dump()
            teams[team["name"]] = team
        return teams

    @property
    def table(self) -> list[dict[str, typing.Any]]:
        teams = [
            {
                "name": team["name"],
                "played": team["played"],
                "wins": team["wins"],
                "draws": team["draws"],
                "losses": team["losses"],
                "goals_for": team["goals_for"],
                "goals_against": team["goals_against"],
                "xg": team["shooting"]["xg"],
                "points": team["points"],
            }
            for team in self.teams.values()
        ]
        table = sorted(teams, key=sort_table_key)
        return table

    @property
    def matches(self) -> dict[str, dict[str, typing.Any]]:
        return {
            match.name: match.model_dump()
            for match in self.response.fotmob.matches
        }

    def teams_index(self) -> list[Params]:
        fotmob = self.response.fotmob.teams
        fbref = self.response.fbref.teams

        params: list[Params] = []
        for fotmob_team in fotmob:
            fbref_team = process.extractOne(
                fotmob_team, fbref, processor=lambda x: x.name
            )[0]

            params.append(
                Params(
                    fotmob_id=fotmob_team.id,
                    fbref_id=fbref_team.id,
                    fbref_path_name=fbref_team.path_name,
                )
            )
        return params
