import typing

from rapidfuzz import process

from .base import ParamsDict, StatDict


class FotMobMatchDict(StatDict):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: StatDict
    home: StatDict
    away: StatDict


class MatchParamsDict(ParamsDict):
    ...


class MatchDict(FotMobMatchDict):
    ...


class InfoDict(typing.TypedDict):
    matches: list[MatchDict]


class Matches:
    def __init__(
        self,
        fotmob: tuple[FotMobMatchDict, ...],
        fbref: tuple[StatDict, ...],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> InfoDict:
        matches = [MatchDict(**match) for match in self.fotmob]
        return {"matches": matches}

    def index(self) -> list[MatchParamsDict]:
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
        params: list[MatchParamsDict] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match["cancelled"]:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x["name"]
                )[0]

                match_params = MatchParamsDict(
                    fotmob_id=fotmob_match["id"], fbref_id=fbref_match["id"]
                )
                params.append(match_params)
        return params
