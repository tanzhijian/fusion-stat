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


class TeamModel(BaseModel):
    id: str
    name: str


class FBrefShootingModel(BaseModel):
    shots: float
    xg: float
