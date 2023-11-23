import typing

import httpx
from pydantic import BaseModel
from rapidfuzz import process

from .base import Collector
from .config import COMPETITIONS
from .models import Stat
from .spiders.fbref import Competitions as FBrefCompetitions
from .spiders.fotmob import Competitions as FotMobCompetitions


class CompetitionParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None
    official_name: str
    season: int | None


class Fusion:
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


class Competitions(Collector[Fusion]):
    def __init__(
        self,
        *,
        season: int | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.season = season

    @property
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobCompetitions(client=self.client).process(),
            FBrefCompetitions(client=self.client).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref = items
        return Fusion(fotmob=fotmob, fbref=fbref, season=self.season)
