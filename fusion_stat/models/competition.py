import typing

from rapidfuzz import process

from . import FBrefShooting, FBrefShootingTypes, Stat, StatTypes


class TeamParamsTypes(typing.TypedDict):
    fotmob_id: str
    fbref_id: str
    fbref_path_name: str | None


class InfoTypes(StatTypes):
    logo: str
    type: str
    season: str
    names: set[str]


class TeamTypes(StatTypes):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int
    logo: str
    shooting: FBrefShootingTypes


class TableTeamTypes(typing.TypedDict):
    name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    xg: float
    points: int


class MatchType(StatTypes):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: StatTypes
    home: StatTypes
    away: StatTypes


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
    def info(self) -> InfoTypes:
        return {
            "id": self.fotmob.id,
            "name": self.fotmob.name,
            "logo": self.official.logo,
            "type": self.fotmob.type,
            "season": self.fotmob.season,
            "names": self.fotmob.names | {self.fbref.name},
        }

    @property
    def teams(self) -> list[TeamTypes]:
        teams: list[TeamTypes] = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]
            official_team = process.extractOne(
                fotmob_team, self.official.teams, processor=lambda x: x.name
            )[0]

            # 稍后来手动解包
            team = TeamTypes(**fotmob_team.model_dump())  # type: ignore
            team["logo"] = official_team.logo
            team["names"] |= fbref_team.names
            team["shooting"] = FBrefShootingTypes(
                **fbref_team.shooting.model_dump()  # type: ignore
            )
            teams.append(team)
        return teams

    @staticmethod
    def sort_table_key(team: TableTeamTypes) -> tuple[int, int, int, str]:
        """1. 首先按照积分降序排序，积分高的排在前面
        2. 如果两个或多个球队的积分相同，则根据以下规则进行排序：
            1. 净胜球降序排序
            2. 如果净胜球也相同，则根据进球数降序排序
            3. 如果进球数也相同，则根据球队的名称（字母顺序）升序排序
        """
        goal_difference = team["goals_for"] - team["goals_against"]
        return (
            -team["points"],
            -goal_difference,
            -team["goals_for"],
            team["name"],
        )

    @property
    def table(self) -> list[TableTeamTypes]:
        teams = [
            TableTeamTypes(
                name=team["name"],
                played=team["played"],
                wins=team["wins"],
                draws=team["draws"],
                losses=team["losses"],
                goals_for=team["goals_for"],
                goals_against=team["goals_against"],
                xg=team["shooting"]["xg"],
                points=team["points"],
            )
            for team in self.teams
        ]
        table = sorted(teams, key=self.sort_table_key)
        return table

    @property
    def matches(self) -> list[MatchType]:
        # 稍后来手动解包
        return [
            MatchType(**match.model_dump())  # type: ignore
            for match in self.fotmob.matches
        ]

    def teams_index(self) -> list[TeamParamsTypes]:
        params: list[TeamParamsTypes] = []
        for fotmob_team in self.fotmob.teams:
            fbref_team = process.extractOne(
                fotmob_team, self.fbref.teams, processor=lambda x: x.name
            )[0]

            team_params = TeamParamsTypes(
                fotmob_id=fotmob_team.id,
                fbref_id=fbref_team.id,
                fbref_path_name=fbref_team.path_name,
            )

            params.append(team_params)
        return params
