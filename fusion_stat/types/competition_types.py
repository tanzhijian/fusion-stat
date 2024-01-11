from .base_types import FBrefShootingDict, ParamsDict, StatDict


class FotMobTeamDict(StatDict):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class FotMobMatchTeamDict(StatDict):
    score: int | None


class FotMobMatchDict(StatDict):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    competition: StatDict
    home: FotMobMatchTeamDict
    away: FotMobMatchTeamDict


class FotMobDict(StatDict):
    type: str
    season: str
    country_code: str
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
    country_code: str
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
