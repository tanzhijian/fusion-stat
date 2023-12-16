import typing

from pydantic import BaseModel
from rapidfuzz import process

from fusion_stat.utils import sort_table_key

from . import FBrefShooting, Stat


class TeamParams(BaseModel):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class FotMobTeam(Stat):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class FotMobMatch(Stat):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Stat
    home: Stat
    away: Stat


class FotMob(Stat):
    type: str
    season: str
    names: set[str]
    teams: tuple[FotMobTeam, ...]
    matches: tuple[FotMobMatch, ...]


class FBrefTeam(Stat):
    path_name: str
    names: set[str]
    shooting: FBrefShooting


class FBref(Stat):
    teams: tuple[FBrefTeam, ...]


class OfficialTeam(Stat):
    logo: str


class Official(Stat):
    logo: str
    teams: tuple[OfficialTeam, ...]


class Competition:
    def __init__(
        self,
        fotmob: FotMob,
        fbref: FBref,
        official: Official,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.official = official

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "id": self.fotmob.id,
            "name": self.fotmob.name,
            "logo": self.official.logo,
            "type": self.fotmob.type,
            "season": self.fotmob.season,
            "names": self.fotmob.names | {self.fbref.name},
        }

    @property
    def teams(self) -> list[dict[str, typing.Any]]:
        teams = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]
            official_team = process.extractOne(
                fotmob_team, self.official.teams, processor=lambda x: x.name
            )[0]

            team = fotmob_team.model_dump()
            team["logo"] = official_team.logo
            team["names"] |= fbref_team.names
            team["shooting"] = fbref_team.shooting.model_dump()
            teams.append(team)
        return teams

    @property
    def table(self) -> list[dict[str, typing.Any]]:
        teams = [
            {
                "name": team["name"],
                "played": team["played"],
                "wins": team["wins"],
                "draws": team["draws"],
                "losses": team["losses"],
                "goals_for": team["goals_for"],
                "goals_against": team["goals_against"],
                "xg": team["shooting"]["xg"],
                "points": team["points"],
            }
            for team in self.teams
        ]
        table = sorted(teams, key=sort_table_key)
        return table

    @property
    def matches(self) -> list[dict[str, typing.Any]]:
        return [match.model_dump() for match in self.fotmob.matches]

    def teams_index(self) -> list[dict[str, typing.Any]]:
        params: list[dict[str, typing.Any]] = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]

            team_params = TeamParams(
                fotmob_id=fotmob_team.id,
                fbref_id=fbref_team.id,
                fbref_path_name=fbref_team.path_name,
            ).model_dump(exclude_none=True)

            params.append(team_params)
        return params
