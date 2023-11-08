import typing

import httpx

from .base import Fusion
from .spiders.fotmob import Match as FotMobMatch
from .spiders.fbref import Match as FBrefMatch
from .models import Stat


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
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobMatch(id=self.fotmob_id, client=self.client).download(),
            FBrefMatch(id=self.fbref_id, client=self.client).download(),
        )

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
