import httpx
from rapidfuzz import process

from fusion_stat.base import Spider
from fusion_stat.config import (
    COMPETITIONS,
    COMPETITIONS_INDEX,
    COMPETITIONS_SIMILARITY_SCORE,
    POSITIONS,
)
from fusion_stat.models import (
    CompetitionFotMob,
    CompetitionFotMobMatch,
    CompetitionFotMobTeam,
    MatchesFotMobMatch,
    MemberFotMob,
    Stat,
    TeamFotMob,
    TeamFotMobMember,
)

BASE_URL = "https://www.fotmob.com/api"


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=BASE_URL + "/allLeagues")

    def parse(self, response: httpx.Response) -> tuple[Stat, ...]:
        json = response.json()
        competitions: list[Stat] = []
        selection = json["popular"]
        for competition in selection:
            name = competition["name"]
            if process.extractOne(
                name,
                COMPETITIONS,
                score_cutoff=COMPETITIONS_SIMILARITY_SCORE,
            ):
                competitions.append(
                    Stat(
                        id=str(competition["id"]),
                        name=name,
                    )
                )
        return tuple(competitions)


class Competition(Spider):
    def __init__(
        self,
        *,
        id: str,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        if season is None:
            self.season = season
        else:
            self.season = f"{season}/{season + 1}"

    @property
    def request(self) -> httpx.Request:
        params = {"id": self.id}
        if self.season is not None:
            params["season"] = self.season
        return httpx.Request(
            "GET",
            url=BASE_URL + "/leagues",
            params=params,
        )

    def parse(self, response: httpx.Response) -> CompetitionFotMob:
        json = response.json()
        name = json["details"]["name"]
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        names = {name, json["details"]["shortName"]}

        teams = []
        for team in json["table"][0]["data"]["table"]["all"]:
            goals_for, goals_against = team["scoresStr"].split("-")
            teams.append(
                CompetitionFotMobTeam(
                    id=str(team["id"]),
                    name=team["name"],
                    names={team["name"], team["shortName"]},
                    played=team["played"],
                    wins=team["wins"],
                    draws=team["draws"],
                    losses=team["losses"],
                    goals_for=int(goals_for),
                    goals_against=int(goals_against),
                    points=int(team["pts"]),
                )
            )

        matches = []
        for match in json["matches"]["allMatches"]:
            home_name = match["home"]["name"]
            away_name = match["away"]["name"]
            matches.append(
                CompetitionFotMobMatch(
                    id=str(match["id"]),
                    name=f"{home_name} vs {away_name}",
                    utc_time=match["status"]["utcTime"],
                    finished=match["status"]["finished"],
                    started=match["status"]["started"],
                    cancelled=match["status"]["cancelled"],
                    score=match["status"].get("scoreStr"),
                    competition=Stat(id=self.id, name=name),
                    home=Stat(
                        id=str(match["home"]["id"]),
                        name=home_name,
                    ),
                    away=Stat(
                        id=str(match["away"]["id"]),
                        name=away_name,
                    ),
                )
            )

        return CompetitionFotMob(
            id=self.id,
            name=name,
            type=type,
            season=season,
            names=names,
            teams=tuple(teams),
            matches=tuple(matches),
        )


class Team(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/teams",
            params={"id": self.id},
        )

    def parse(self, response: httpx.Response) -> TeamFotMob:
        json = response.json()
        id = str(json["details"]["id"])
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}

        members = []
        for role in json["squad"]:
            for member in role[1]:
                position = member.get("role")
                if position:
                    position = POSITIONS[position]
                members.append(
                    TeamFotMobMember(
                        id=str(member["id"]),
                        name=member["name"],
                        country=member["cname"],
                        country_code=member["ccode"],
                        position=position,
                        is_staff=position is None,
                    )
                )

        return TeamFotMob(
            id=id,
            name=name,
            names=names,
            members=tuple(members),
        )


class Member(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/playerData",
            params={"id": self.id},
        )

    def parse(self, response: httpx.Response) -> MemberFotMob:
        json = response.json()
        name = json["name"]
        country = json["meta"]["personJSONLD"]["nationality"]["name"]
        position = json["origin"]["positionDesc"]["primaryPosition"]["label"]
        is_staff = position == "Coach"
        return MemberFotMob(
            id=self.id,
            name=name,
            country=country,
            position=position,
            is_staff=is_staff,
        )


class Matches(Spider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.date = date.replace("-", "")

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/matches",
            params={"date": self.date},
        )

    def parse(
        self, response: httpx.Response
    ) -> tuple[MatchesFotMobMatch, ...]:
        json = response.json()
        matches = []
        competitions_id = {c["fotmob_id"] for c in COMPETITIONS_INDEX}
        for competition in json["leagues"]:
            if (competition_id := str(competition["id"])) in competitions_id:
                for match in competition["matches"]:
                    home_name = match["home"]["longName"]
                    away_name = match["away"]["longName"]
                    matches.append(
                        MatchesFotMobMatch(
                            id=str(match["id"]),
                            name=f"{home_name} vs {away_name}",
                            utc_time=match["status"]["utcTime"],
                            finished=match["status"]["finished"],
                            started=match["status"]["started"],
                            cancelled=match["status"]["cancelled"],
                            score=match["status"].get("scoreStr"),
                            competition=Stat(
                                id=competition_id, name=competition["name"]
                            ),
                            home=Stat(
                                id=str(match["home"]["id"]),
                                name=home_name,
                            ),
                            away=Stat(
                                id=str(match["away"]["id"]),
                                name=away_name,
                            ),
                        )
                    )
        return tuple(matches)


class Match(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/matchDetails",
            params={"matchId": self.id},
        )

    def parse(self, response: httpx.Response) -> Stat:
        json = response.json()
        home_team, away_team = json["header"]["teams"]
        home_name = home_team["name"]
        away_name = away_team["name"]
        return Stat(id=self.id, name=f"{home_name} vs {away_name}")
