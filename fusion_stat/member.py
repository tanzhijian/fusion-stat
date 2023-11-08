import typing

import httpx

from .base import Fusion
from .spiders.fotmob import Member as FotMobMember
from .spiders.fbref import Member as FBrefMember
from .models import MemberFotMob, MemberFBref


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
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobMember(id=self.fotmob_id, client=self.client).download(),
            FBrefMember(
                id=self.fbref_id,
                path_name=self.fbref_path_name,
                client=self.client,
            ).download(),
        )

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
