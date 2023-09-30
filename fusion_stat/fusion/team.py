import typing

import httpx
from pydantic import BaseModel
from parsel import Selector

from .base import FusionStat
from fusion_stat.clients import FotMob, FBref
from fusion_stat.clients.base import Client
from fusion_stat.utils import unpack_params, get_element_text
from fusion_stat.models import Params, Stat


class FotMobTeamModel(Stat):
    names: set[str]


class FBrefTeamModel(Stat):
    names: set[str]


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
    def _clients_cls(self) -> list[type[Client]]:
        return [FotMob, FBref]

    async def _create_task(
        self, client_cls: type[Client], client: httpx.AsyncClient
    ) -> httpx.Response:
        session = client_cls(client=client, **self.kwargs)
        team = await session.get_team(self.params)
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
        return FotMobTeamModel(id=id, name=name, names=names)

    def _parse_fbref(self, text: str) -> FBrefTeamModel:
        selector = Selector(text)
        h1 = get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])
        return FBrefTeamModel(
            id=self.params.fbref_id,
            name=team_name,
            names={team_name},
        )

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.response.fotmob.name,
            "names": self.response.fotmob.names | self.response.fbref.names,
        }
