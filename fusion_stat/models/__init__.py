import typing

from pydantic import BaseModel


class StatTypes(typing.TypedDict):
    id: str
    name: str


class FBrefShootingTypes(typing.TypedDict):
    shots: float
    xg: float


class Stat(BaseModel):
    id: str
    name: str


class FBrefShooting(BaseModel):
    shots: float = 0
    xg: float = 0
