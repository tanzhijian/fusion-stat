import typing

import httpx
from rapidfuzz import process
from pydantic import BaseModel

from .base import Fusion, Spider
from .spiders.fotmob import Team as FotMobTeam
from .spiders.fbref import Team as FBrefTeam
from .utils import fuzzy_similarity_mean
from .config import MEMBERS_SIMILARITY_SCORE
from .models import TeamFotMob, TeamFBref


class FotMobParams(BaseModel):
    id: str


class FBrefParams(BaseModel):
    id: str
    path_name: str | None


class Params(BaseModel):
    fotmob: FotMobParams
    fbref: FBrefParams


class MemberParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class Response:
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


class Team(Fusion[Response]):
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
    def params(self) -> BaseModel:
        fotmob = FotMobParams(id=self.fotmob_id)
        fbref = FBrefParams(id=self.fbref_id, path_name=self.fbref_path_name)
        return Params(fotmob=fotmob, fbref=fbref)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobTeam, FBrefTeam)

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
