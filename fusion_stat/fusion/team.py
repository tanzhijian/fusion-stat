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


class FBrefMemberModel(Stat):
    shooting: FBrefShooting


class FotMobTeamModel(Stat):
    names: set[str]
    members: list[FotMobMemberModel]


class FBrefTeamModel(Stat):
    names: set[str]
    shooting: FBrefShooting
    members: list[FBrefMemberModel]


class Response(BaseModel):
    fotmob: FotMobTeamModel
    fbref: FBrefTeamModel


class Team(FusionStat[Response]):
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
        team = await downloader.get_team(self.params)
        return team

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

    def _parse_fotmob(self, json: typing.Any) -> FotMobTeamModel:
        id = str(json["details"]["id"])
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}

        members = []
        for role in json["squad"]:
            for member in role[1:]:
                members.append(
                    FotMobMemberModel(
                        id=str(member[0]["id"]),
                        name=member[0]["name"],
                        country=member[0]["cname"],
                        is_staff=member[0].get("role") is None,
                    )
                )

        return FotMobTeamModel(id=id, name=name, names=names, members=members)

    def _parse_fbref(self, text: str) -> FBrefTeamModel:
        selector = Selector(text)
        h1 = get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])

        table = selector.xpath('//table[starts-with(@id,"stats_shooting_")]')
        team_shooting = parse_fbref_shooting(table.xpath("./tfoot/tr[1]"))

        members = []
        trs = table.xpath("./tbody/tr")
        for tr in trs:
            href = get_element_text(tr.xpath("./th/a/@href"))
            name = get_element_text(tr.xpath("./th/a/text()"))
            shooting = parse_fbref_shooting(tr)
            members.append(
                FBrefMemberModel(
                    id=href.split("/")[3], name=name, shooting=shooting
                )
            )

        return FBrefTeamModel(
            id=self.params.fbref_id,
            name=team_name,
            names={team_name},
            shooting=team_shooting,
            members=members,
        )

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.response.fotmob.name,
            "names": self.response.fotmob.names | self.response.fbref.names,
        }
