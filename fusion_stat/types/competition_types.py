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


class _BaseMathchDict(StatDict):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    competition: StatDict


class FotMobMatchDict(_BaseMathchDict):
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
    country_code: str
    logo: str


class OfficialDict(StatDict):
    logo: str
    teams: list[OfficialTeamDict]


class TransfermarktTeamDict(StatDict):
    market_values: str
    path_name: str


class TransfermarktDict(StatDict):
    market_values: str
    player_average_market_value: str
    teams: list[TransfermarktTeamDict]


class InfoDict(StatDict):
    names: set[str]
    logo: str
    type: str
    season: str
    country_code: str
    market_values: str
    player_average_market_value: str


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
    country_code: str
    market_values: str
    names: set[str]
    shooting: FBrefShootingDict


class TableTeamDict(_BaseTeamDict):
    xg: float


class MatchTeamDict(FotMobMatchTeamDict):
    ...


class MatchDict(_BaseMathchDict):
    home: MatchTeamDict
    away: MatchTeamDict


class TeamParamsDict(ParamsDict):
    fbref_path_name: str
    transfermarkt_id: str
    transfermarkt_path_name: str
