from pydantic import BaseModel


class Params(BaseModel):
    fotmob_id: str

    fbref_id: str
    fbref_path_name: str | None = None


class Stat(BaseModel):
    id: str
    name: str


class FBrefShooting(BaseModel):
    shots: float
    xg: float
