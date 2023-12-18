import typing

from rapidfuzz import process

from fusion_stat.config import MEMBERS_SIMILARITY_SCORE
from fusion_stat.utils import fuzzy_similarity_mean

from . import FBrefShooting, FBrefShootingTypes, Stat


class MemberParamsTypes(typing.TypedDict):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class InfoTypes(typing.TypedDict):
    name: str
    names: set[str]


class StaffTypes(typing.TypedDict):
    name: str
    country: str


class PlayerTypes(typing.TypedDict):
    name: str
    names: set[str]
    country: str
    position: str | None
    shooting: FBrefShootingTypes


class FotMobMember(Stat):
    country: str
    country_code: str
    position: str | None
    is_staff: bool


class FotMob(Stat):
    names: set[str]
    members: tuple[FotMobMember, ...]


class FBrefMember(Stat):
    names: set[str]
    path_name: str
    country_code: str
    position: str
    shooting: FBrefShooting


class FBref(Stat):
    names: set[str]
    shooting: FBrefShooting
    members: tuple[FBrefMember, ...]


class Team:
    def __init__(
        self,
        fotmob: FotMob,
        fbref: FBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> InfoTypes:
        return {
            "name": self.fotmob.name,
            "names": self.fotmob.names | self.fbref.names,
        }

    @property
    def staff(self) -> list[StaffTypes]:
        return [
            {"name": member.name, "country": member.country}
            for member in self.fotmob.members
            if member.is_staff
        ]

    @property
    def players(self) -> list[PlayerTypes]:
        players: list[PlayerTypes] = []
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

                    # 稍后来手动解包
                    shooting = FBrefShootingTypes(
                        **fbref_member.shooting.model_dump(),  # type: ignore
                    )
                    players.append(
                        PlayerTypes(
                            name=fotmob_member.name,
                            names={fotmob_member.name} | fbref_member.names,
                            country=fotmob_member.country,
                            position=fotmob_member.position,
                            shooting=shooting,
                        )
                    )
                except TypeError:
                    pass

        return players

    def members_index(self) -> list[MemberParamsTypes]:
        params: list[MemberParamsTypes] = []
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
                    member_params = MemberParamsTypes(
                        fotmob_id=fotmob_member.id,
                        fbref_id=fbref_member.id,
                        fbref_path_name=fbref_member.path_name,
                    )
                    params.append(member_params)
                except TypeError:
                    pass
        return params
