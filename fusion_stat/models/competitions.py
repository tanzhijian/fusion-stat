from rapidfuzz import process

from fusion_stat.config import COMPETITIONS

from . import CompetitionParams, Stat


class PremierLeagueCompetition(Stat):
    seasons: tuple[Stat, ...]


class Competitions:
    def __init__(
        self,
        fotmob: tuple[Stat, ...],
        fbref: tuple[Stat, ...],
        season: int | None = None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.season = season

    def index(self) -> list[CompetitionParams]:
        params: list[CompetitionParams] = []

        for fotmob_competition in self.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.fbref,
                processor=lambda x: x["name"],
            )[0]
            official_name = process.extractOne(
                fotmob_competition["name"], COMPETITIONS.keys()
            )[0]

            competition_params = CompetitionParams(
                fotmob_id=fotmob_competition["id"],
                fbref_id=fbref_competition["id"],
                fbref_path_name=fbref_competition["name"].replace(" ", "-"),
                official_name=official_name,
            )
            if self.season is not None:
                competition_params["season"] = self.season

            params.append(competition_params)

        return params
