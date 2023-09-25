import typing

import httpx
from httpx._types import ProxiesTypes
from rapidfuzz import process

from .base import FusionStat
from ._utils import get_element_text, parse_fbref_shooting
from fusion_stat.clients.base import Client
from fusion_stat.config import COMPETITIONS
from fusion_stat.models import CompetitionModel, TeamModel, FBrefShootingModel


class CompetitionDetailsModel(CompetitionModel):
    type: str
    season: str
    names: set[str]


class FotMobTeamModel(TeamModel):
    names: set[str]


class FBrefTeamModel(TeamModel):
    shooting: FBrefShootingModel


class Competition(FusionStat):
    def __init__(
        self,
        id: str,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(httpx_client_cls, proxies)
        if id not in COMPETITIONS:
            raise KeyError(
                f"Please enter a valid id: {tuple(COMPETITIONS.keys())}"
            )
        self.id = id

    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        async with client_cls(
            httpx_client_cls=self.httpx_client_cls,
            proxies=self.proxies,
        ) as client:
            competition = await client.get_competition(self.id)
        return competition

    @property
    def info(self) -> dict[str, str]:
        name = self.response.fotmob["details"]["name"]
        fbref_h1 = get_element_text(self.response.fbref.xpath("//h1/text()"))

        competition = CompetitionDetailsModel(
            id=self.id,
            name=name,
            type=self.response.fotmob["details"]["type"],
            season=self.response.fotmob["details"]["selectedSeason"],
            names={
                name,
                self.response.fotmob["details"]["shortName"],
                " ".join(fbref_h1.split(" ")[1:-1]),
            },
        )
        return competition.model_dump()

    @property
    def teams(self) -> list[dict[str, typing.Any]]:
        fotmob = self._parse_fotmob_teams()
        fbref = self._parse_fbref_teams()

        teams = []
        for fotmob_team in fotmob:
            fbref_team = process.extractOne(
                fotmob_team, fbref, processor=lambda x: x.name
            )[0]

            team = {
                "name": fotmob_team.name,
                "shots": fbref_team.shooting.shots,
                "xg": fbref_team.shooting.xg,
            }
            teams.append(team)
        return teams

    def _parse_fotmob_teams(self) -> list[FotMobTeamModel]:
        teams = [
            FotMobTeamModel(
                id=str(team["id"]),
                name=team["name"],
                names={team["name"], team["shortName"]},
            )
            for team in self.response.fotmob["table"][0]["data"]["table"][
                "all"
            ]
        ]
        return teams

    def _parse_fbref_teams(self) -> list[FBrefTeamModel]:
        teams = []
        trs = self.response.fbref.xpath(
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
        return teams
