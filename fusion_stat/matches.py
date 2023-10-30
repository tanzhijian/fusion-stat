import typing

import httpx
from rapidfuzz import process

from .base import Fusion, Spider
from .spiders.fotmob import Matches as FotMobMatches
from .spiders.fbref import Matches as FBrefMatches
from .models import Params, Stat, MatchesFotMobMatch


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

    def index(self) -> list[Params]:
        params = []
        for fotmob_match in self.fotmob:
            if not fotmob_match.cancelled:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x.name
                )[0]
                params.append(
                    Params(fotmob_id=fotmob_match.id, fbref_id=fbref_match.id)
                )
        return params


class Matches(Fusion[Response]):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(
        self,
        date: str,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.date = date

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobMatches, FBrefMatches)

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **{"date": self.date},
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
