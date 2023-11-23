import typing

import httpx

from .base import Collector
from .models import MemberFBref, MemberFotMob
from .spiders.fbref import Member as FBrefMember
from .spiders.fotmob import Member as FotMobMember


class Fusion:
    def __init__(
        self,
        fotmob: MemberFotMob,
        fbref: MemberFBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Member(Collector[Fusion]):
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
            FotMobMember(id=self.fotmob_id, client=self.client).process(),
            FBrefMember(
                id=self.fbref_id,
                path_name=self.fbref_path_name,
                client=self.client,
            ).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref = items
        return Fusion(fotmob=fotmob, fbref=fbref)
