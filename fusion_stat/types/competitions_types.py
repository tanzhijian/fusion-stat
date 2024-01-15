import typing

from .base_types import ParamsDict, StatDict


class FBrefCompetitionDict(StatDict):
    path_name: str
    country_code: str


class PremierLeagueCompetitionDict(StatDict):
    seasons: list[StatDict]


class TransfermarktCompetitionDict(StatDict):
    path_name: str


class InfoDict(typing.TypedDict):
    count: int
    names: list[str]


class CompetitionDict(StatDict):
    fotmob: StatDict
    fbref: FBrefCompetitionDict
    transfermarkt: TransfermarktCompetitionDict


class BaseCompetitionParamsDict(ParamsDict):
    transfermarkt_id: str


class _CompetitionParamsDict(BaseCompetitionParamsDict):
    fbref_path_name: str
    official_name: str
    transfermarkt_path_name: str


class CompetitionParamsDict(_CompetitionParamsDict, total=False):
    season: int | None
