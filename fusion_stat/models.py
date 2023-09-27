from pydantic import BaseModel


class Feature(BaseModel):
    id: str


class FBrefFeature(Feature):
    path_name: str


class Params(BaseModel):
    fotmob: Feature
    fbref: FBrefFeature


class CompetitionModel(BaseModel):
    id: str
    name: str
