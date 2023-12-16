import typing

from pydantic import BaseModel
from rapidfuzz import process

from fusion_stat.config import COMPETITIONS

from . import Stat


class CompetitionParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None
    official_name: str
    season: int | None


class PremierLeagueCompetition(Stat):
    seasons: tuple[Stat, ...]


class Competitions:
    def __init__(
        self,
        fotmob: tuple[Stat, ...],
        fbref: tuple[Stat, ...],
        season: int | None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.season = season

    def index(self) -> list[dict[str, typing.Any]]:
        params: list[dict[str, typing.Any]] = []

        for fotmob_competition in self.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.fbref,
                processor=lambda x: x.name,
            )[0]
            official_name = process.extractOne(
                fotmob_competition.name, COMPETITIONS
            )[0]

            competition_params = CompetitionParams(
                fotmob_id=fotmob_competition.id,
                fbref_id=fbref_competition.id,
                fbref_path_name=fbref_competition.name.replace(" ", "-"),
                official_name=official_name,
                season=self.season,
            ).model_dump(exclude_none=True)

            params.append(competition_params)

        return params
