from .base_types import FBrefShootingDict, ParamsDict, StatDict


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
