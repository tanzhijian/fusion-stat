from pydantic import BaseModel


class Stat(BaseModel):
    id: str
    name: str


class Response(BaseModel):
    fotmob: tuple[Stat, ...]
    fbref: tuple[Stat, ...]


class Feature(BaseModel):
    id: str


class FBrefFeature(Feature):
    path_name: str


class Params(BaseModel):
    fotmob: Feature
    fbref: FBrefFeature


class CompetitionModel(Stat):
    ...
