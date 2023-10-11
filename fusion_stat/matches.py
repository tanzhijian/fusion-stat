import typing

import httpx
from parsel import Selector
from pydantic import BaseModel

from .base import FusionStat
from .downloaders import FotMob, FBref
from .downloaders.base import Downloader
from .utils import get_element_text
from .models import Stat


class FotMobMatchModel(Stat):
    ...


class FBrefMatchModel(Stat):
    ...


class Response(BaseModel):
    fotmob: tuple[FotMobMatchModel, ...]
    fbref: tuple[FBrefMatchModel, ...]


class Matches(FusionStat[Response]):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(
        self,
        date: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client, **kwargs)
        self.date = date

    @property
    def _downloaders_cls(self) -> list[type[Downloader]]:
        return [FotMob, FBref]

    async def _create_task(
        self, downloader_cls: type[Downloader], client: httpx.AsyncClient
    ) -> httpx.Response:
        downloader = downloader_cls(client=client, **self.kwargs)
        matches = await downloader.get_matches(self.date)
        return matches

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

    def _parse_fotmob(self, json: typing.Any) -> tuple[FotMobMatchModel, ...]:
        matches = []
        for league in json["leagues"]:
            for match in league["matches"]:
                home_name = match["home"]["longName"]
                away_name = match["away"]["longName"]
                matches.append(
                    FotMobMatchModel(
                        id=str(match["id"]),
                        name=f"{home_name} vs {away_name}",
                    )
                )
        return tuple(matches)

    def _parse_fbref(self, text: str) -> tuple[FBrefMatchModel, ...]:
        selector = Selector(text)
        matches = []
        trs = selector.xpath('//table[starts-with(@id,"sched_")]/tbody/tr')
        # 如果还没有进行的比赛会找不到对应节点
        for tr in trs:
            try:
                home_name = get_element_text(
                    tr.xpath('./td[@data-stat="home_team"]/a/text()')
                )
                away_name = get_element_text(
                    tr.xpath('./td[@data-stat="away_team"]/a/text()')
                )

                href = get_element_text(
                    tr.xpath('./td[@data-stat="score"]/a/@href')
                )
                id = href.split("/")[3]
                matches.append(
                    FBrefMatchModel(
                        id=id,
                        name=f"{home_name} vs {away_name}",
                    )
                )
            except ValueError:
                pass
        return tuple(matches)
