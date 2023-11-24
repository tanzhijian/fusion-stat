import typing

import httpx
from pydantic import BaseModel
from rapidfuzz import process

from .base import Collector
from .models import MatchesFotMobMatch, Stat
from .spiders.fbref import Matches as FBrefMatches
from .spiders.fotmob import Matches as FotMobMatches


class MatchParams(BaseModel):
    fotmob_id: str
    fbref_id: str


class Fusion:
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
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
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


class Matches(Collector[Fusion]):
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
            FotMobMatches(date=self.date, client=self.client).process(),
            FBrefMatches(date=self.date, client=self.client).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref = items
        return Fusion(fotmob=fotmob, fbref=fbref)
