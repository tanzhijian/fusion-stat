import typing

import httpx
from rapidfuzz import process
from pydantic import BaseModel

from .base import Fusion
from .spiders.fotmob import Matches as FotMobMatches
from .spiders.fbref import Matches as FBrefMatches
from .models import Stat, MatchesFotMobMatch


class MatchParams(BaseModel):
    fotmob_id: str
    fbref_id: str


class Response:
    def __init__(
        self,
        fotmob: tuple[MatchesFotMobMatch, ...],
        fbref: tuple[Stat, ...],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "matches": [match.model_dump() for match in self.fotmob],
        }

    def index(self) -> list[dict[str, typing.Any]]:
        params: list[dict[str, typing.Any]] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match.cancelled:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x.name
                )[0]
                match_params = MatchParams(
                    fotmob_id=fotmob_match.id, fbref_id=fbref_match.id
                ).model_dump(exclude_none=True)
                params.append(match_params)
        return params


class Matches(Fusion[Response]):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(
        self,
        *,
        date: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.date = date

    @property
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobMatches(date=self.date, client=self.client).download(),
            FBrefMatches(date=self.date, client=self.client).download(),
        )

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
