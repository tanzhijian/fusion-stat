import typing

import httpx
from rapidfuzz import process

from .base import Fusion
from fusion_stat.utils import unpack_params, sort_table_key
from .downloaders.base import Spider
from .downloaders.fotmob import Competition as FotMobCompetition
from .downloaders.fbref import Competition as FBrefCompetition
from .models import Params, CompetitionFotMob, CompetitionFBref


class Response:
    def __init__(
        self,
        fotmob: CompetitionFotMob,
        fbref: CompetitionFBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.fotmob.name,
            "type": self.fotmob.type,
            "season": self.fotmob.season,
            "names": self.fotmob.names | {self.fbref.name},
        }

    @property
    def teams(self) -> list[dict[str, typing.Any]]:
        teams = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]

            team = fotmob_team.model_dump()
            team["names"] |= fbref_team.names
            team["shooting"] = fbref_team.shooting.model_dump()
            teams.append(team)
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
            for team in self.teams
        ]
        table = sorted(teams, key=sort_table_key)
        return table

    @property
    def matches(self) -> list[dict[str, typing.Any]]:
        return [match.model_dump() for match in self.fotmob.matches]

    def teams_index(self) -> list[Params]:
        params: list[Params] = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]

            params.append(
                Params(
                    fotmob_id=fotmob_team.id,
                    fbref_id=fbref_team.id,
                    fbref_path_name=fbref_team.path_name,
                )
            )
        return params


class Competition(Fusion[Response]):
    def __init__(
        self,
        params: Params | dict[str, str],
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.params = unpack_params(params)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobCompetition, FBrefCompetition)

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **self.params[spider_cls.module_name],
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
