from .base_types import FBrefShootingDict, StatDict


class FotMobDict(StatDict):
    country: str
    is_staff: bool
    position: str


class FBrefDict(StatDict):
    shooting: FBrefShootingDict
