import typing

import httpx
from rapidfuzz import process

from .base import FusionStat
from .downloaders.base import Spider
from .downloaders.fotmob import Competitions as FotMobCompetitions
from .downloaders.fbref import Competitions as FBrefCompetitions
from .models import Params, Stat


class Competitions(FusionStat):
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

    async def _create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(client=client, **self.kwargs)
        response = await spider.download()
        return response

    def index(self) -> list[Params]:
        fotmob_competitions: tuple[Stat, ...] = self.responses[0]
        fbref_competitions: tuple[Stat, ...] = self.responses[1]
        params: list[Params] = []

        for fotmob_competition in fotmob_competitions:
            fbref_competition = process.extractOne(
                fotmob_competition,
                fbref_competitions,
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
