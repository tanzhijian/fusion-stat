import typing

from pydantic import BaseModel


class StatTypes(typing.TypedDict):
    id: str
    name: str


class _BaseCompetitionParamsTypes(typing.TypedDict):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None
    official_name: str


class CompetitionParamsTypes(_BaseCompetitionParamsTypes, total=False):
    season: int | None


class FBrefShootingTypes(typing.TypedDict):
    shots: float
    xg: float


class Stat(BaseModel):
    id: str
    name: str


class FBrefShooting(BaseModel):
    shots: float = 0
    xg: float = 0
