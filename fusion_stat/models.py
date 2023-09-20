from pydantic import BaseModel


class Competition(BaseModel):
    id: str
    name: str


class Competitions(BaseModel):
    fotmob: list[Competition]
    fbref: list[Competition]
