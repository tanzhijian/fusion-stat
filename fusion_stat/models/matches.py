import typing

from rapidfuzz import process

from . import Stat, StatTypes


class MatchParamsTypes(typing.TypedDict):
    fotmob_id: str
    fbref_id: str


class InfoMatchTypes(StatTypes):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: StatTypes
    home: StatTypes
    away: StatTypes


class InfoTypes(typing.TypedDict):
    matches: list[InfoMatchTypes]


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
    def info(self) -> InfoTypes:
        # 稍后来手动解包
        matches = [
            InfoMatchTypes(**match.model_dump())  # type: ignore
            for match in self.fotmob
        ]
        return {"matches": matches}

    def index(self) -> list[MatchParamsTypes]:
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
        params: list[MatchParamsTypes] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match.cancelled:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x.name
                )[0]

                match_params = MatchParamsTypes(
                    fotmob_id=fotmob_match.id, fbref_id=fbref_match.id
                )
                params.append(match_params)
        return params
