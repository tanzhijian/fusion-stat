import typing

from .base_types import ParamsDict, StatDict


class FBrefCompetitionDict(StatDict):
    country_code: str


class PremierLeagueCompetitionDict(StatDict):
    seasons: list[StatDict]


class TransfermarktCompetitionDict(StatDict):
    path_name: str


class _BaseCompetitionParamsDict(ParamsDict):
    fbref_path_name: str | None
    official_name: str


class InfoDict(typing.TypedDict):
    count: int
    names: list[str]


class CompetitionDict(StatDict):
    fotmob: StatDict
    fbref: FBrefCompetitionDict


class CompetitionParamsDict(_BaseCompetitionParamsDict, total=False):
    season: int | None
