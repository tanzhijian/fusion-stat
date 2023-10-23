import typing

import httpx
from parsel import Selector
from pydantic import BaseModel

from .base import FusionStat
from .downloaders import FotMob, FBref
from .downloaders.base import Downloader
from .utils import unpack_params
from .models import Stat, Params


class FotMobMatchModel(Stat):
    ...


class FBrefMatchModel(Stat):
    ...


class Response(BaseModel):
    fotmob: FotMobMatchModel
    fbref: FBrefMatchModel


class Match(FusionStat[Response]):
    def __init__(
        self,
        params: Params | dict[str, str],
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client, **kwargs)
        self.params = unpack_params(params)

    @property
    def _downloaders_cls(self) -> list[type[Downloader]]:
        return [FotMob, FBref]

    async def _create_task(
        self, downloader_cls: type[Downloader], client: httpx.AsyncClient
    ) -> httpx.Response:
        downloader = downloader_cls(client=client, **self.kwargs)
        match = await downloader.get_match(**self.params[downloader.name])
        return match

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

    def _parse_fotmob(self, json: typing.Any) -> FotMobMatchModel:
        id = self.params["fotmob"]["id"]
        home_team, away_team = json["header"]["teams"]
        home_name = home_team["name"]
        away_name = away_team["name"]
        return FotMobMatchModel(id=id, name=f"{home_name} vs {away_name}")

    def _parse_fbref(self, text: str) -> FBrefMatchModel:
        selector = Selector(text)
        home_name, away_name = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return FBrefMatchModel(
            id=self.params["fbref"]["id"],
            name=f"{home_name} vs {away_name}",
        )
