import typing

import httpx
from pydantic import BaseModel
from parsel import Selector
from rapidfuzz import process

from .base import FusionStat
from .downloaders import FotMob, FBref
from .downloaders.base import Downloader
from .utils import unpack_params, get_element_text, parse_fbref_shooting
from .config import MEMBERS_SIMILARITY_SCORE, POSITIONS
from .models import Params, Stat, FBrefShooting


class FotMobMemberModel(Stat):
    country: str
    country_code: str
    position: str | None
    is_staff: bool


class FBrefMemberModel(Stat):
    country_code: str
    position: str
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
            for member in role[1]:
                position = member.get("role")
                if position:
                    position = POSITIONS[position]
                members.append(
                    FotMobMemberModel(
                        id=str(member["id"]),
                        name=member["name"],
                        country=member["cname"],
                        country_code=member["ccode"],
                        position=position,
                        is_staff=position is None,
                    )
                )

        return FotMobTeamModel(id=id, name=name, names=names, members=members)

    def _parse_fbref(self, text: str) -> FBrefTeamModel:
        selector = Selector(text)
        h1 = get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])

        standard_stats_table = selector.xpath(
            '//table[starts-with(@id,"stats_standard_")]'
        )
        shooting_table = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]'
        )
        team_shooting = parse_fbref_shooting(
            shooting_table.xpath("./tfoot/tr[1]")
        )

        players_shooting: dict[str, FBrefShooting] = {}
        for tr in shooting_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            id = href.split("/")[3]
            shooting = parse_fbref_shooting(tr)
            players_shooting[id] = shooting

        players = []
        for tr in standard_stats_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            id = href.split("/")[3]
            name = get_element_text(tr.xpath("./th/a/text()"))
            country_code = get_element_text(
                tr.xpath('./td[@data-stat="nationality"]/a/@href')
            ).split("/")[3]

            position = get_element_text(
                tr.xpath('./td[@data-stat="position"]/text()')
            )

            try:
                shooting = players_shooting[id]
            except KeyError:
                shooting = FBrefShooting()
            players.append(
                FBrefMemberModel(
                    id=id,
                    name=name,
                    country_code=country_code,
                    position=position,
                    shooting=shooting,
                )
            )

        return FBrefTeamModel(
            id=self.params.fbref_id,
            name=team_name,
            names={team_name},
            shooting=team_shooting,
            members=players,
        )

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.response.fotmob.name,
            "names": self.response.fotmob.names | self.response.fbref.names,
        }

    @property
    def staff(self) -> list[dict[str, typing.Any]]:
        return [
            {"name": member.name, "country": member.country}
            for member in self.response.fotmob.members
            if member.is_staff
        ]

    @property
    def players(self) -> list[dict[str, typing.Any]]:
        fotmob = self.response.fotmob.members
        fbref = self.response.fbref.members

        players = []
        for fotmob_member in fotmob:
            if not fotmob_member.is_staff:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        fbref,
                        processor=lambda x: x.name,
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    players.append(
                        {
                            "name": fotmob_member.name,
                            "country": fotmob_member.country,
                            "shooting": fbref_member.shooting.model_dump(),
                        }
                    )
                except TypeError:
                    pass

        return players
