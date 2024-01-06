from rapidfuzz import process

from fusion_stat.config import COMPETITIONS

from .base import ParamsDict, StatDict


class PremierLeagueCompetitionDict(StatDict):
    seasons: tuple[StatDict, ...]


class _BaseCompetitionParamsDict(ParamsDict):
    fbref_path_name: str | None
    official_name: str


class CompetitionParamsDict(_BaseCompetitionParamsDict, total=False):
    season: int | None


class Competitions:
    def __init__(
        self,
        fotmob: tuple[StatDict, ...],
        fbref: tuple[StatDict, ...],
        season: int | None = None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.season = season

    def index(self) -> list[CompetitionParamsDict]:
        params: list[CompetitionParamsDict] = []

        for fotmob_competition in self.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.fbref,
                processor=lambda x: x["name"],
            )[0]
            official_name = process.extractOne(
                fotmob_competition["name"],
                COMPETITIONS.keys(),
            )[0]

            competition_params = CompetitionParamsDict(
                fotmob_id=fotmob_competition["id"],
                fbref_id=fbref_competition["id"],
                fbref_path_name=fbref_competition["name"].replace(" ", "-"),
                official_name=official_name,
            )
            if self.season is not None:
                competition_params["season"] = self.season

            params.append(competition_params)

        return params
