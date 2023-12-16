from pydantic import BaseModel


class Stat(BaseModel):
    id: str
    name: str


class FBrefShooting(BaseModel):
    shots: float = 0
    xg: float = 0
