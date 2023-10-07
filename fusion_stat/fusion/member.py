import typing

import httpx
from pydantic import BaseModel
from parsel import Selector

from .base import FusionStat
from fusion_stat.downloaders import FotMob, FBref
from fusion_stat.downloaders.base import Downloader
from fusion_stat.utils import (
    unpack_params,
    get_element_text,
    parse_fbref_shooting,
)
from fusion_stat.models import Params, Stat, FBrefShooting


class FotMobMemberModel(Stat):
    country: str
    is_staff: bool
    position: str


class FBrefMemberModel(Stat):
    shooting: FBrefShooting


class Response(BaseModel):
    fotmob: FotMobMemberModel
    fbref: FBrefMemberModel


class Member(FusionStat[Response]):
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
        player = await downloader.get_member(self.params)
        return player

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

    def _parse_fotmob(self, json: typing.Any) -> FotMobMemberModel:
        name = json["name"]
        country = json["meta"]["personJSONLD"]["nationality"]["name"]
        position = json["origin"]["positionDesc"]["primaryPosition"]["label"]
        is_staff = position == "Coach"
        return FotMobMemberModel(
            id=self.params.fotmob_id,
            name=name,
            country=country,
            position=position,
            is_staff=is_staff,
        )

    def _parse_fbref(self, text: str) -> FBrefMemberModel:
        selector = Selector(text)
        name = get_element_text(selector.xpath("//h1/span/text()"))

        tr = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]/tfoot/tr[1]'
        )
        shooting = parse_fbref_shooting(tr)

        return FBrefMemberModel(
            id=self.params.fbref_id, name=name, shooting=shooting
        )
