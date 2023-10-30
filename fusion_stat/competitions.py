import typing

import httpx
from rapidfuzz import process

from .base import Fusion, Spider
from .spiders.fotmob import Competitions as FotMobCompetitions
from .spiders.fbref import Competitions as FBrefCompetitions
from .models import Params, Stat


class Response:
    def __init__(
        self,
        fotmob: tuple[Stat, ...],
        fbref: tuple[Stat, ...],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    def index(self) -> list[Params]:
        params: list[Params] = []

        for fotmob_competition in self.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.fbref,
                processor=lambda x: x.name,
            )[0]

            params.append(
                Params(
                    fotmob_id=fotmob_competition.id,
                    fbref_id=fbref_competition.id,
                    fbref_path_name=fbref_competition.name.replace(" ", "-"),
                )
            )

        return params


class Competitions(Fusion[Response]):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobCompetitions, FBrefCompetitions)

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(client=client, **self.kwargs)
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
