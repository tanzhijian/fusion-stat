import typing

import httpx
from pydantic import BaseModel

from .base import Fusion, Spider
from .spiders.fotmob import Match as FotMobMatch
from .spiders.fbref import Match as FBrefMatch
from .models import Stat


class FotMobParams(BaseModel):
    id: str


class FBrefParams(BaseModel):
    id: str


class Params(BaseModel):
    fotmob: FotMobParams
    fbref: FBrefParams


class Response:
    def __init__(
        self,
        fotmob: Stat,
        fbref: Stat,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Match(Fusion[Response]):
    def __init__(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.fotmob_id = fotmob_id
        self.fbref_id = fbref_id

    @property
    def params(self) -> BaseModel:
        fotmob = FotMobParams(id=self.fotmob_id)
        fbref = FBrefParams(id=self.fbref_id)
        return Params(fotmob=fotmob, fbref=fbref)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobMatch, FBrefMatch)

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
