import asyncio
import typing

import httpx
from httpx._types import ProxiesTypes
from parsel import Selector
from pydantic import BaseModel
from rapidfuzz import process

from ._utils import get_element_text, parse_fbref_shooting
from fusion_stat.clients.base import Client
from fusion_stat.clients import FotMob, FBref
from fusion_stat.models import (
    Stat,
    Params,
    FBrefShooting,
)


class FotMobTeamModel(Stat):
    names: set[str]


class FBrefTeamModel(Stat):
    shooting: FBrefShooting


class FotMobCompetitionModel(Stat):
    type: str
    season: str
    names: set[str]
    teams: tuple[FotMobTeamModel, ...]


class FBrefCompetitionModel(Stat):
    teams: tuple[FBrefTeamModel, ...]


class Response(BaseModel):
    fotmob: FotMobCompetitionModel
    fbref: FBrefCompetitionModel


class Competition:
    def __init__(
        self,
        params: Params,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        self.httpx_client_cls = httpx_client_cls
        self.proxies = proxies
        self._response: Response | None = None
        self.params = params

    @property
    def response(self) -> Response:
        if self._response is None:
            raise ValueError("Confirm get() has been executed")
        return self._response

    @response.setter
    def response(self, value: Response) -> None:
        self._response = value

    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        async with client_cls(
            httpx_client_cls=self.httpx_client_cls,
            proxies=self.proxies,
        ) as client:
            competition = await client.get_competition(self.params)
        return competition

    async def get(self) -> Response:
        tasks = [
            self._create_task(FotMob),
            self._create_task(FBref),
        ]
        fotmob, fbref = await asyncio.gather(*tasks)

        fotmob_competition = self._parse_fotmob(fotmob.json())
        fbref_competition = self._parse_fbref(fbref.text)
        self.response = Response(
            fotmob=fotmob_competition, fbref=fbref_competition
        )
        return self.response

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

            team = {
                "name": fotmob_team.name,
                "names": fotmob_team.names | {fbref_team.name},
                "shooting": fbref_team.shooting.model_dump(),
            }
            teams[fotmob_team.name] = team
        return teams

    def _parse_fotmob(self, json: typing.Any) -> FotMobCompetitionModel:
        name = json["details"]["name"]
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        names = {name, json["details"]["shortName"]}

        teams = [
            FotMobTeamModel(
                id=str(team["id"]),
                name=team["name"],
                names={team["name"], team["shortName"]},
            )
            for team in json["table"][0]["data"]["table"]["all"]
        ]
        return FotMobCompetitionModel(
            id=self.params.fotmob_id,
            name=name,
            type=type,
            season=season,
            names=names,
            teams=tuple(teams),
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
            href = get_element_text(tr.xpath("./th/a/@href"))
            name = get_element_text(tr.xpath("./th/a/text()"))
            shooting = parse_fbref_shooting(tr)
            teams.append(
                FBrefTeamModel(
                    id=href.split("/")[3],
                    name=name,
                    shooting=shooting,
                )
            )
        return FBrefCompetitionModel(
            id=self.params.fbref_id,
            name=competition_name,
            teams=tuple(teams),
        )
