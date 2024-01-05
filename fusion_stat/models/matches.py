import typing

from rapidfuzz import process

from . import Stat


class MatchParams(typing.TypedDict):
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


class InfoMatch(FotMobMatch):
    ...


class Info(typing.TypedDict):
    matches: list[InfoMatch]


class Matches:
    def __init__(
        self,
        fotmob: tuple[FotMobMatch, ...],
        fbref: tuple[Stat, ...],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> Info:
        matches = [InfoMatch(**match) for match in self.fotmob]
        return {"matches": matches}

    def index(self) -> list[MatchParams]:
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
        params: list[MatchParams] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match["cancelled"]:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x["name"]
                )[0]

                match_params = MatchParams(
                    fotmob_id=fotmob_match["id"], fbref_id=fbref_match["id"]
                )
                params.append(match_params)
        return params
