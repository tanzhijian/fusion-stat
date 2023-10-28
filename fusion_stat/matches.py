import typing

import httpx
from rapidfuzz import process

from .base import FusionStat
from .downloaders.base import Spider
from .downloaders.fotmob import Matches as FotMobMatches
from .downloaders.fbref import Matches as FBrefMatches
from .models import Params, Stat, MatchesFotMobMatch


class Matches(FusionStat):
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

    async def _create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **{"date": self.date},
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response

    @property
    def info(self) -> dict[str, typing.Any]:
        fotmob_matches: tuple[MatchesFotMobMatch, ...] = self.responses[0]
        return {
            "date": self.date,
            "matches": [match.model_dump() for match in fotmob_matches],
        }

    def index(self) -> list[Params]:
        fotmob_matches: tuple[MatchesFotMobMatch, ...] = self.responses[0]
        fbref_matches: tuple[Stat, ...] = self.responses[1]

        params = []
        for fotmob_match in fotmob_matches:
            if not fotmob_match.cancelled:
                fbref_match = process.extractOne(
                    fotmob_match, fbref_matches, processor=lambda x: x.name
                )[0]
                params.append(
                    Params(fotmob_id=fotmob_match.id, fbref_id=fbref_match.id)
                )
        return params
