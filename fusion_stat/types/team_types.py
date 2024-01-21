from .base_types import FBrefShootingDict, ParamsDict, StatDict


class BaseMemberDict(StatDict):
    country_code: str
    position: str | None


class FotMobMemberDict(BaseMemberDict):
    country: str
    is_staff: bool


class FotMobDict(StatDict):
    names: set[str]
    country_code: str
    members: list[FotMobMemberDict]


class FBrefMemberDict(BaseMemberDict):
    names: set[str]
    path_name: str
    shooting: FBrefShootingDict


class FBrefDict(StatDict):
    names: set[str]
    shooting: FBrefShootingDict
    members: list[FBrefMemberDict]


class TransfermarktMemberDict(BaseMemberDict):
    date_of_birth: str
    market_values: str
    path_name: str


class TransfermarktDict(StatDict):
    market_values: str
    members: list[TransfermarktMemberDict]


class InfoDict(StatDict):
    names: set[str]
    country_code: str
    market_values: str


class StaffDict(StatDict):
    country: str


class PlayerDict(StatDict):
    names: set[str]
    country: str
    position: str | None
    date_of_birth: str
    market_values: str
    shooting: FBrefShootingDict


class MemberParamsDict(ParamsDict):
    fbref_path_name: str
    transfermarkt_id: str
    transfermarkt_path_name: str
