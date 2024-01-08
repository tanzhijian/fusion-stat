import typing

from .base_types import ParamsDict, StatDict


class FotMobTeamDict(StatDict):
    score: int | None


class FotMobMatchDict(StatDict):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    competition: StatDict
    home: FotMobTeamDict
    away: FotMobTeamDict


class MatchDict(FotMobMatchDict):
    ...


class InfoDict(typing.TypedDict):
    count: int


class MatchParamsDict(ParamsDict):
    ...
