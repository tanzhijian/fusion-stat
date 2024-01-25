from .base_types import FBrefShootingDict, StatDict


class FotMobDict(StatDict):
    country: str
    position: str


class FBrefDict(StatDict):
    shooting: FBrefShootingDict


class TransfermarktDict(StatDict):
    market_values: str
