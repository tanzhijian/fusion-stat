import typing

import httpx
from pydantic import BaseModel
from rapidfuzz import process

from .base import Collector
from .models import CompetitionFBref, CompetitionFotMob, CompetitionOfficial
from .spiders.fbref import Competition as FBrefCompetition
from .spiders.fotmob import Competition as FotMobCompetition
from .spiders.official import Competition as OfficialCompetition
from .utils import sort_table_key


class TeamParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class Fusion:
    def __init__(
        self,
        fotmob: CompetitionFotMob,
        fbref: CompetitionFBref,
        official: CompetitionOfficial,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.official = official

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "id": self.fotmob.id,
            "name": self.fotmob.name,
            "logo": self.official.logo,
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
            official_team = process.extractOne(
                fotmob_team, self.official.teams, processor=lambda x: x.name
            )[0]

            team = fotmob_team.model_dump()
            team["logo"] = official_team.logo
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


class Competition(Collector[Fusion]):
    def __init__(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        official_name: str,
        season: int | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.fotmob_id = fotmob_id
        self.fbref_id = fbref_id
        self.fbref_path_name = fbref_path_name
        self.official_name = official_name
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
            ).process(),
            FBrefCompetition(
                id=self.fbref_id,
                path_name=self.fbref_path_name,
                season=self.season,
                client=self.client,
            ).process(),
            OfficialCompetition(
                name=self.official_name,
                season=self.season,
                client=self.client,
            ).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref, official = items
        return Fusion(fotmob=fotmob, fbref=fbref, official=official)
