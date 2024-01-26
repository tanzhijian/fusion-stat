from .base_types import FBrefShootingDict, ParamsDict, StatDict


class BasePlayerDict(StatDict):
    country_code: str
    position: str | None


class FotMobPlayerDict(BasePlayerDict):
    country: str


class FotMobStaffDict(StatDict):
    country: str
    country_code: str


class FotMobDict(StatDict):
    names: set[str]
    country_code: str
    staff: FotMobStaffDict
    players: list[FotMobPlayerDict]


class FBrefPlayerDict(BasePlayerDict):
    names: set[str]
    path_name: str
    shooting: FBrefShootingDict


class FBrefDict(StatDict):
    names: set[str]
    shooting: FBrefShootingDict
    players: list[FBrefPlayerDict]


class TransfermarktPlayerDict(BasePlayerDict):
    date_of_birth: str
    market_values: str
    path_name: str


class TransfermarktStaffDict(StatDict):
    position: str
    path_name: str


class TransfermarktDict(StatDict):
    market_values: str
    players: list[TransfermarktPlayerDict]


class InfoDict(StatDict):
    names: set[str]
    country_code: str
    market_values: str


class StaffDict(FotMobStaffDict):
    ...


class PlayerDict(StatDict):
    names: set[str]
    country: str
    position: str | None
    date_of_birth: str
    market_values: str
    shooting: FBrefShootingDict


class PlayerParamsDict(ParamsDict):
    fbref_path_name: str
    transfermarkt_id: str
    transfermarkt_path_name: str
