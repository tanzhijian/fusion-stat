import typing

from parsel import Selector
from pydantic import BaseModel


class Response:
    def __init__(self, *, fotmob: typing.Any, fbref: str) -> None:
        self.fotmob = fotmob
        self.fbref = Selector(fbref)


class CompetitionModel(BaseModel):
    id: str
    name: str


class CompetitionDetailsModel(CompetitionModel):
    type: str
    season: str
    names: set[str]


class FotMobTeamModel(BaseModel):
    id: str
    name: str
    names: set[str]


class FBrefShootingModel(BaseModel):
    shots: float
    xg: float


class FBrefTeamModel(BaseModel):
    id: str
    name: str
    shooting: FBrefShootingModel
