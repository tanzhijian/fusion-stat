from pydantic import BaseModel


class Competition(BaseModel):
    id: str
    name: str


class Competitions(BaseModel):
    fotmob: list[Competition]
    fbref: list[Competition]


class Team(BaseModel):
    id: str
    name: str
    names: set[str]
    shooting: int


class CompetitionDetails(Competition):
    type: str
    season: str
    names: set[str]
    teams: list[Team]
