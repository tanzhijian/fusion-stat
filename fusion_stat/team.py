import typing

import httpx
from rapidfuzz import process

from .base import FusionStat
from .downloaders.base import Spider
from .downloaders.fotmob import Team as FotMobTeam
from .downloaders.fbref import Team as FBrefTeam
from .utils import (
    unpack_params,
    fuzzy_similarity_mean,
)
from .config import MEMBERS_SIMILARITY_SCORE
from .models import Params, TeamFotMob, TeamFBref


class Team(FusionStat):
    def __init__(
        self,
        params: Params | dict[str, str],
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.params = unpack_params(params)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobTeam, FBrefTeam)

    async def _create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **self.params[spider_cls.module_name],
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response

    @property
    def info(self) -> dict[str, typing.Any]:
        fotmob: TeamFotMob = self.responses[0]
        fbref: TeamFBref = self.responses[1]
        return {
            "name": fotmob.name,
            "names": fotmob.names | fbref.names,
        }

    @property
    def staff(self) -> list[dict[str, typing.Any]]:
        fotmob: TeamFotMob = self.responses[0]

        return [
            {"name": member.name, "country": member.country}
            for member in fotmob.members
            if member.is_staff
        ]

    @property
    def players(self) -> list[dict[str, typing.Any]]:
        fotmob: TeamFotMob = self.responses[0]
        fbref: TeamFBref = self.responses[1]

        players = []
        for fotmob_member in fotmob.members:
            if not fotmob_member.is_staff:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        fbref.members,
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x.name,
                            x.country_code,
                            x.position,
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    players.append(
                        {
                            "name": fotmob_member.name,
                            "names": {fotmob_member.name} | fbref_member.names,
                            "country": fotmob_member.country,
                            "position": fotmob_member.position,
                            "shooting": fbref_member.shooting.model_dump(),
                        }
                    )
                except TypeError:
                    pass

        return players

    def members_index(self) -> list[Params]:
        fotmob: TeamFotMob = self.responses[0]
        fbref: TeamFBref = self.responses[1]

        params: list[Params] = []
        for fotmob_member in fotmob.members:
            if not fotmob_member.is_staff:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        fbref.members,
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x.name,
                            x.country_code,
                            x.position,
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    params.append(
                        Params(
                            fotmob_id=fotmob_member.id,
                            fbref_id=fbref_member.id,
                            fbref_path_name=fbref_member.path_name,
                        )
                    )
                except TypeError:
                    pass
        return params
