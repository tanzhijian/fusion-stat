import typing

import httpx
from pydantic import BaseModel

from .base import Fusion, Spider
from .spiders.fotmob import Member as FotMobMember
from .spiders.fbref import Member as FBrefMember
from .models import MemberFotMob, MemberFBref


class FotMobParams(BaseModel):
    id: str


class FBrefParams(BaseModel):
    id: str
    path_name: str | None


class Params(BaseModel):
    fotmob: FotMobParams
    fbref: FBrefParams


class Response:
    def __init__(
        self,
        fotmob: MemberFotMob,
        fbref: MemberFBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Member(Fusion[Response]):
    def __init__(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.fotmob_id = fotmob_id
        self.fbref_id = fbref_id
        self.fbref_path_name = fbref_path_name

    @property
    def params(self) -> BaseModel:
        fotmob = FotMobParams(id=self.fotmob_id)
        fbref = FBrefParams(id=self.fbref_id, path_name=self.fbref_path_name)
        return Params(fotmob=fotmob, fbref=fbref)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobMember, FBrefMember)

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
