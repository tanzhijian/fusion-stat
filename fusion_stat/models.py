from pydantic import BaseModel, Field


class Params(BaseModel):
    fotmob_id: str

    fbref_id: str
    fbref_path_name: str | None = None


class Stat(BaseModel):
    id: str = Field(exclude=True)
    name: str


class FBrefShooting(BaseModel):
    shots: float = 0
    xg: float = 0


# competition
class CompetitionFotMobTeam(Stat):
    names: set[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class CompetitionFotMobMatch(Stat):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Stat
    home: Stat
    away: Stat


class CompetitionFotMob(Stat):
    type: str
    season: str
    names: set[str]
    teams: tuple[CompetitionFotMobTeam, ...]
    matches: tuple[CompetitionFotMobMatch, ...]


class CompetitionFBrefTeam(Stat):
    path_name: str
    names: set[str]
    shooting: FBrefShooting


class CompetitionFBref(Stat):
    teams: tuple[CompetitionFBrefTeam, ...]


# team
class TeamFotMobMember(Stat):
    country: str
    country_code: str
    position: str | None
    is_staff: bool


class TeamFotMob(Stat):
    names: set[str]
    members: tuple[TeamFotMobMember, ...]


class TeamFBrefMember(Stat):
    names: set[str]
    path_name: str
    country_code: str
    position: str
    shooting: FBrefShooting


class TeamFBref(Stat):
    names: set[str]
    shooting: FBrefShooting
    members: tuple[TeamFBrefMember, ...]


# member
class MemberFotMob(Stat):
    country: str
    is_staff: bool
    position: str


class MemberFBref(Stat):
    shooting: FBrefShooting


# matches
class MatchesFotMobMatch(Stat):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    score: str | None
    competition: Stat
    home: Stat
    away: Stat


# match
