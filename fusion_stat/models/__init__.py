import typing


class StatDict(typing.TypedDict):
    id: str
    name: str


class _BaseCompetitionParamsDict(typing.TypedDict):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None
    official_name: str


class CompetitionParamsDict(_BaseCompetitionParamsDict, total=False):
    season: int | None


class FBrefShootingDict(typing.TypedDict):
    shots: float
    xg: float
