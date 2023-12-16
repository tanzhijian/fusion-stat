import typing

from pydantic import BaseModel
from rapidfuzz import process

from . import Stat


class MatchParams(BaseModel):
    fotmob_id: str
    fbref_id: str


class FotMobMatch(Stat):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Stat
    home: Stat
    away: Stat


class Matches:
    def __init__(
        self,
        fotmob: tuple[FotMobMatch, ...],
        fbref: tuple[Stat, ...],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "matches": [match.model_dump() for match in self.fotmob],
        }

    def index(self) -> list[dict[str, typing.Any]]:
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
        params: list[dict[str, typing.Any]] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match.cancelled:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x.name
                )[0]
                match_params = MatchParams(
                    fotmob_id=fotmob_match.id, fbref_id=fbref_match.id
                ).model_dump(exclude_none=True)
                params.append(match_params)
        return params
