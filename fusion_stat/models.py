from pydantic import BaseModel


class Stat(BaseModel):
    id: str
    name: str


class Feature(BaseModel):
    id: str


class FBrefFeature(Feature):
    path_name: str


class Params(BaseModel):
    fotmob: Feature
    fbref: FBrefFeature


class FBrefShooting(BaseModel):
    shots: float
    xg: float
