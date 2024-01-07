import typing

from fusion_stat.config import COMPETITIONS

from .base import ParamsDict, StatDict


class PremierLeagueCompetitionDict(StatDict):
    seasons: list[StatDict]


class _BaseCompetitionParamsDict(ParamsDict):
    fbref_path_name: str | None
    official_name: str


class InfoDict(typing.TypedDict):
    count: int
    names: list[str]


class CompetitionDict(StatDict):
    fotmob: StatDict
    fbref: StatDict


class CompetitionParamsDict(_BaseCompetitionParamsDict, total=False):
    season: int | None


class Competitions:
    def __init__(
        self,
        fotmob: list[StatDict],
        fbref: list[StatDict],
        season: int | None = None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.season = season

    @property
    def info(self) -> InfoDict:
        """
        Return a dict that includes the following keys:

        * count (int): number of competitions
        * names (list[str]): names of competitions
        """
        return InfoDict(
            count=len(COMPETITIONS),
            names=list(COMPETITIONS.keys()),
        )

    @property
    def items(self) -> list[CompetitionDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): fotmob competition id
        * name (str): config competition name
        * fotmob (dict): fotmob competition
                * id (str): fotmob competition id
                * name (str): fotmob competition name
        * fbref (dict): fbref competition
                * id (str): fbref competition id
                * name (str): fbref competition name
        """
        items: list[CompetitionDict] = []
        for name, params in COMPETITIONS.items():
            fotmob_competition = self._find_competition_by_id(
                self.fotmob, params["fotmob_id"]
            )
            fbref_competition = self._find_competition_by_id(
                self.fbref, params["fbref_id"]
            )
            item = CompetitionDict(
                id=params["fotmob_id"],
                name=name,
                fotmob=fotmob_competition,
                fbref=fbref_competition,
            )
            items.append(item)
        return items

    def _find_competition_by_id(
        self, competitions: list[StatDict], competition_id: str
    ) -> StatDict:
        for competition in competitions:
            if competition["id"] == competition_id:
                return competition
        raise ValueError(f"Competition with id {competition_id} not found")

    def get_params(self) -> list[CompetitionParamsDict]:
        """
        Return a list of dicts that include the following keys:

            * fotmob_id (str): fotmob competition id
            * fbref_id (str): fbref competition id
            * fbref_path_name (str): fbref competition path name
            * official_name (str): config competition name
            * season (int, optional): fotmob competition season
        """
        params: list[CompetitionParamsDict] = []

        for item in self.items:
            competition_params = CompetitionParamsDict(
                fotmob_id=item["fotmob"]["id"],
                fbref_id=item["fbref"]["id"],
                fbref_path_name=item["fbref"]["name"].replace(" ", "-"),
                official_name=item["name"],
            )

            if self.season is not None:
                competition_params["season"] = self.season

            params.append(competition_params)

        return params
