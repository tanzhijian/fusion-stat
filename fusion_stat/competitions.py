import typing

import httpx
from rapidfuzz import process
from pydantic import BaseModel

from .base import Fusion
from .spiders.fotmob import Competitions as FotMobCompetitions
from .spiders.fbref import Competitions as FBrefCompetitions
from .models import Stat


class CompetitionParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None
    season: int | None


class Response:
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

            competition_params = CompetitionParams(
                fotmob_id=fotmob_competition.id,
                fbref_id=fbref_competition.id,
                fbref_path_name=fbref_competition.name.replace(" ", "-"),
                season=self.season,
            ).model_dump(exclude_none=True)

            params.append(competition_params)

        return params


class Competitions(Fusion[Response]):
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
            FotMobCompetitions(client=self.client).download(),
            FBrefCompetitions(client=self.client).download(),
        )

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref, season=self.season)
