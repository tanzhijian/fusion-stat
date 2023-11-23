import typing

import httpx

from .base import Collector
from .models import Stat
from .spiders.fbref import Match as FBrefMatch
from .spiders.fotmob import Match as FotMobMatch


class Fusion:
    def __init__(
        self,
        fotmob: Stat,
        fbref: Stat,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Match(Collector[Fusion]):
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
            FotMobMatch(id=self.fotmob_id, client=self.client).process(),
            FBrefMatch(id=self.fbref_id, client=self.client).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref = items
        return Fusion(fotmob=fotmob, fbref=fbref)
