import typing

import httpx

from fusion_stat.base import Spider
from .premierleague import Competition as PremierLeagueCompetition
from .laliga import Competition as LaLigaCompetition
from .bundesliga import Competition as BundesligaCompetition


spiders_cls: dict[str, type[Spider]] = {
    "Premier League": PremierLeagueCompetition,
    "La Liga": LaLigaCompetition,
    "Bundesliga": BundesligaCompetition,
}


class Competition(Spider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.name = name
        self.season = season
        self.spider = spiders_cls[self.name](
            **{"name": self.name, "season": self.season}, client=self.client
        )

    @property
    def request(self) -> httpx.Request:
        return self.spider.request

    def parse(self, response: httpx.Response) -> typing.Any:
        return self.spider.parse(response)
