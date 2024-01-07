from rapidfuzz import process

from .base import FBrefShootingDict, ParamsDict, StatDict


class FotMobTeamDict(StatDict):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class FotMobMatchDict(StatDict):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: StatDict
    home: StatDict
    away: StatDict


class FotMobDict(StatDict):
    type: str
    season: str
    names: set[str]
    teams: list[FotMobTeamDict]
    matches: list[FotMobMatchDict]


class FBrefTeamDict(StatDict):
    path_name: str
    names: set[str]
    shooting: FBrefShootingDict


class FBrefDict(StatDict):
    teams: list[FBrefTeamDict]


class OfficialTeamDict(StatDict):
    logo: str


class OfficialDict(StatDict):
    logo: str
    teams: list[OfficialTeamDict]


class InfoDict(StatDict):
    logo: str
    type: str
    season: str
    names: set[str]


class _BaseTeamDict(StatDict):
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int
    logo: str


class TeamDict(_BaseTeamDict):
    names: set[str]
    shooting: FBrefShootingDict


class TableTeamDict(_BaseTeamDict):
    xg: float


class MatchDict(FotMobMatchDict):
    ...


class TeamParamsDict(ParamsDict):
    fbref_path_name: str | None


class Competition:
    def __init__(
        self,
        fotmob: FotMobDict,
        fbref: FBrefDict,
        official: OfficialDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.official = official

    @property
    def info(self) -> InfoDict:
        """
        Return a dict that includes the following keys:

        * id (str): competition id.
        * name (str): competition name.
        * logo (str): Competition logo.
        * type (str): Competition type.
        * season (str): Competition season.
        * names (set[str]): All competition names.
        """
        return {
            "id": self.fotmob["id"],
            "name": self.fotmob["name"],
            "logo": self.official["logo"],
            "type": self.fotmob["type"],
            "season": self.fotmob["season"],
            "names": self.fotmob["names"] | {self.fbref["name"]},
        }

    @property
    def teams(self) -> list[TeamDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): team id.
        * name (str): team name.
        * names (set[str]): All team names.
        * played (int): number of matches played.
        * wins (int): number of matches won.
        * draws (int): number of matches drawn.
        * losses (int): number of matches lost.
        * goals_for (int): number of goals scored.
        * goals_against (int): number of goals conceded.
        * points (int): number of points.
        * logo (str): team logo.
        * shooting (dict): shooting data.
                * shots (int): number of shots.
                * xg (float): expected goals.
        """
        teams: list[TeamDict] = []
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = process.extractOne(
                fotmob_team,
                self.fbref["teams"],
                processor=lambda x: x["name"],
            )[0]
            official_team = process.extractOne(
                fotmob_team,
                self.official["teams"],
                processor=lambda x: x["name"],
            )[0]

            team = TeamDict(
                **fotmob_team,
                logo=official_team["logo"],
                shooting=fbref_team["shooting"],
            )
            team["names"] |= fbref_team["names"]
            teams.append(team)
        return teams

    @staticmethod
    def sort_table_key(team: TableTeamDict) -> tuple[int, int, int, str]:
        """
        1. 首先按照积分降序排序，积分高的排在前面
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
    def table(self) -> list[TableTeamDict]:
        """
        Return a list of dicts sorted by the standings that include the following keys:

        * id (str): team id.
        * name (str): team name.
        * played (int): number of matches played.
        * wins (int): number of matches won.
        * draws (int): number of matches drawn.
        * losses (int): number of matches lost.
        * goals_for (int): number of goals scored.
        * goals_against (int): number of goals conceded.
        * points (int): number of points.
        * xg (float): expected goals.
        * logo (str): team logo.
        """
        teams = [
            TableTeamDict(
                id=team["id"],
                name=team["name"],
                played=team["played"],
                wins=team["wins"],
                draws=team["draws"],
                losses=team["losses"],
                goals_for=team["goals_for"],
                goals_against=team["goals_against"],
                points=team["points"],
                xg=team["shooting"]["xg"],
                logo=team["logo"],
            )
            for team in self.teams
        ]
        table = sorted(teams, key=self.sort_table_key)
        return table

    @property
    def matches(self) -> list[MatchDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): match id.
        * name (str): match name.
        * utc_time (str): match kickoff time.
        * finished (bool): whether the match is finished or not.
        * started (bool): whether the match has started or not.
        * cancelled (bool): whether the match is cancelled or not.
        * score (str): match score.
        * competition (dict): competition data.
                * id (str): competition id.
                * name (str): competition name.
        * home (dict): home team data.
                * id (str): team id.
                * name (str): team name.
        * away (dict): away team data.
                * id (str): team id.
                * name (str): team name.
        """
        return [MatchDict(**match) for match in self.fotmob["matches"]]

    def get_teams_params(self) -> list[TeamParamsDict]:
        params: list[TeamParamsDict] = []
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = process.extractOne(
                fotmob_team,
                self.fbref["teams"],
                processor=lambda x: x["name"],
            )[0]

            team_params = TeamParamsDict(
                fotmob_id=fotmob_team["id"],
                fbref_id=fbref_team["id"],
                fbref_path_name=fbref_team["path_name"],
            )

            params.append(team_params)
        return params
