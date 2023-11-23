import typing

import httpx
from pydantic import BaseModel
from rapidfuzz import process

from .base import Collector
from .config import MEMBERS_SIMILARITY_SCORE
from .models import TeamFBref, TeamFotMob
from .spiders.fbref import Team as FBrefTeam
from .spiders.fotmob import Team as FotMobTeam
from .utils import fuzzy_similarity_mean


class MemberParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class Fusion:
    def __init__(
        self,
        fotmob: TeamFotMob,
        fbref: TeamFBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "name": self.fotmob.name,
            "names": self.fotmob.names | self.fbref.names,
        }

    @property
    def staff(self) -> list[dict[str, typing.Any]]:
        return [
            {"name": member.name, "country": member.country}
            for member in self.fotmob.members
            if member.is_staff
        ]

    @property
    def players(self) -> list[dict[str, typing.Any]]:
        players = []
        for fotmob_member in self.fotmob.members:
            if not fotmob_member.is_staff:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref.members,
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

    def members_index(self) -> list[dict[str, typing.Any]]:
        params: list[dict[str, typing.Any]] = []
        for fotmob_member in self.fotmob.members:
            if not fotmob_member.is_staff:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref.members,
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x.name,
                            x.country_code,
                            x.position,
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    member_params = MemberParams(
                        fotmob_id=fotmob_member.id,
                        fbref_id=fbref_member.id,
                        fbref_path_name=fbref_member.path_name,
                    ).model_dump(exclude_none=True)
                    params.append(member_params)
                except TypeError:
                    pass
        return params


class Team(Collector[Fusion]):
    def __init__(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.fotmob_id = fotmob_id
        self.fbref_id = fbref_id
        self.fbref_path_name = fbref_path_name

    @property
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (
            FotMobTeam(id=self.fotmob_id, client=self.client).process(),
            FBrefTeam(
                id=self.fbref_id,
                path_name=self.fbref_path_name,
                client=self.client,
            ).process(),
        )

    def parse(self, items: list[typing.Any]) -> Fusion:
        fotmob, fbref = items
        return Fusion(fotmob=fotmob, fbref=fbref)
