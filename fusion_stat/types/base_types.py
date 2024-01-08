import typing


class StatDict(typing.TypedDict):
    id: str
    name: str


class ParamsDict(typing.TypedDict):
    fotmob_id: str
    fbref_id: str


class FBrefShootingDict(typing.TypedDict):
    shots: int
    xg: float
