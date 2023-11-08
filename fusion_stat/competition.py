import typing

import httpx
from rapidfuzz import process
from pydantic import BaseModel

from .base import Fusion
from .spiders.fotmob import Competition as FotMobCompetition
from .spiders.fbref import Competition as FBrefCompetition
from .utils import sort_table_key
from .models import CompetitionFotMob, CompetitionFBref


class TeamParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class Response:
    def __init__(
        self,
        fotmob: CompetitionFotMob,
        fbref: CompetitionFBref,
        season: int | None,
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

    def teams_index(self) -> list[dict[str, typing.Any]]:
        params: list[dict[str, typing.Any]] = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]

            team_params = TeamParams(
                fotmob_id=fotmob_team.id,
                fbref_id=fbref_team.id,
                fbref_path_name=fbref_team.path_name,
            ).model_dump(exclude_none=True)

            params.append(team_params)
        return params


class Competition(Fusion[Response]):
    def __init__(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        season: int | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.fotmob_id = fotmob_id
        self.fbref_id = fbref_id
        self.fbref_path_name = fbref_path_name
        self.season = season

    @property
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobCompetition(
                id=self.fotmob_id,
                season=self.season,
                client=self.client,
            ).download(),
            FBrefCompetition(
                id=self.fbref_id,
                path_name=self.fbref_path_name,
                season=self.season,
                client=self.client,
            ).download(),
        )

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref, season=self.season)
