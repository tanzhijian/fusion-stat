from rapidfuzz import process

from fusion_stat.config import MEMBERS_SIMILARITY_SCORE
from fusion_stat.utils import fuzzy_similarity_mean

from .base import FBrefShootingDict, ParamsDict, StatDict


class FotMobMemberDict(StatDict):
    country: str
    country_code: str
    position: str | None
    is_staff: bool


class FotMobDict(StatDict):
    names: set[str]
    members: list[FotMobMemberDict]


class FBrefMemberDict(StatDict):
    names: set[str]
    path_name: str
    country_code: str
    position: str
    shooting: FBrefShootingDict


class FBrefDict(StatDict):
    names: set[str]
    shooting: FBrefShootingDict
    members: list[FBrefMemberDict]


class InfoDict(StatDict):
    names: set[str]


class StaffDict(StatDict):
    country: str


class PlayerDict(StatDict):
    names: set[str]
    country: str
    position: str | None
    shooting: FBrefShootingDict


class MemberParamsDict(ParamsDict):
    fbref_path_name: str | None


class Team:
    def __init__(
        self,
        fotmob: FotMobDict,
        fbref: FBrefDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> InfoDict:
        return {
            "id": self.fotmob["id"],
            "name": self.fotmob["name"],
            "names": self.fotmob["names"] | self.fbref["names"],
        }

    @property
    def staff(self) -> list[StaffDict]:
        return [
            {
                "id": member["id"],
                "name": member["name"],
                "country": member["country"],
            }
            for member in self.fotmob["members"]
            if member["is_staff"]
        ]

    @property
    def players(self) -> list[PlayerDict]:
        players: list[PlayerDict] = []
        for fotmob_member in self.fotmob["members"]:
            if not fotmob_member["is_staff"]:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref["members"],
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x["name"],
                            x["country_code"],
                            x["position"],
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]

                    shooting = fbref_member["shooting"]
                    players.append(
                        PlayerDict(
                            id=fotmob_member["id"],
                            name=fotmob_member["name"],
                            names={fotmob_member["name"]}
                            | fbref_member["names"],
                            country=fotmob_member["country"],
                            position=fotmob_member["position"],
                            shooting=shooting,
                        )
                    )
                except TypeError:
                    pass

        return players

    def get_members_params(self) -> list[MemberParamsDict]:
        params: list[MemberParamsDict] = []
        for fotmob_member in self.fotmob["members"]:
            if not fotmob_member["is_staff"]:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref["members"],
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x["name"],
                            x["country_code"],
                            x["position"],
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    member_params = MemberParamsDict(
                        fotmob_id=fotmob_member["id"],
                        fbref_id=fbref_member["id"],
                        fbref_path_name=fbref_member["path_name"],
                    )
                    params.append(member_params)
                except TypeError:
                    pass
        return params
