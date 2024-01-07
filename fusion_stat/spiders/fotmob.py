import httpx

from fusion_stat.base import Spider
from fusion_stat.config import COMPETITIONS, POSITIONS
from fusion_stat.models.base import StatDict
from fusion_stat.models.competition import FotMobDict as FotMobCompetitionDict
from fusion_stat.models.competition import (
    FotMobMatchDict as FotMobCompetitionMatchDict,
)
from fusion_stat.models.competition import (
    FotMobTeamDict as FotMobCompetitionTeamDict,
)
from fusion_stat.models.matches import FotMobMatchDict as FotMobMatchesMatchDict
from fusion_stat.models.member import FotMobDict as FotMobMemberDict
from fusion_stat.models.team import FotMobDict as FotMobTeamDict
from fusion_stat.models.team import FotMobMemberDict as FotMobTeamMemberDict

BASE_URL = "https://www.fotmob.com/api"


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=BASE_URL + "/allLeagues")

    def parse(self, response: httpx.Response) -> list[StatDict]:
        json = response.json()
        competitions: list[StatDict] = []
        competitions_id = {
            params["fotmob_id"] for params in COMPETITIONS.values()
        }
        selection = json["popular"]
        for competition in selection:
            if (id := str(competition["id"])) in competitions_id:
                competitions.append(
                    StatDict(
                        id=id,
                        name=competition["name"],
                    )
                )
        return competitions


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

    def parse(self, response: httpx.Response) -> FotMobCompetitionDict:
        json = response.json()
        name = json["details"]["name"]
        type = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        names = {name, json["details"]["shortName"]}

        teams = []
        for team in json["table"][0]["data"]["table"]["all"]:
            goals_for, goals_against = team["scoresStr"].split("-")
            teams.append(
                FotMobCompetitionTeamDict(
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
                FotMobCompetitionMatchDict(
                    id=str(match["id"]),
                    name=f"{home_name} vs {away_name}",
                    utc_time=match["status"]["utcTime"],
                    finished=match["status"]["finished"],
                    started=match["status"]["started"],
                    cancelled=match["status"]["cancelled"],
                    score=match["status"].get("scoreStr"),
                    competition=StatDict(id=self.id, name=name),
                    home=StatDict(
                        id=str(match["home"]["id"]),
                        name=home_name,
                    ),
                    away=StatDict(
                        id=str(match["away"]["id"]),
                        name=away_name,
                    ),
                )
            )

        return FotMobCompetitionDict(
            id=self.id,
            name=name,
            type=type,
            season=season,
            names=names,
            teams=teams,
            matches=matches,
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

    def parse(self, response: httpx.Response) -> FotMobTeamDict:
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
                    FotMobTeamMemberDict(
                        id=str(member["id"]),
                        name=member["name"],
                        country=member["cname"],
                        country_code=member["ccode"],
                        position=position,
                        is_staff=position is None,
                    )
                )

        return FotMobTeamDict(
            id=id,
            name=name,
            names=names,
            members=members,
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

    def parse(self, response: httpx.Response) -> FotMobMemberDict:
        json = response.json()
        name = json["name"]
        country = json["meta"]["personJSONLD"]["nationality"]["name"]
        position = json["origin"]["positionDesc"]["primaryPosition"]["label"]
        is_staff = position == "Coach"
        return FotMobMemberDict(
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

    def parse(self, response: httpx.Response) -> list[FotMobMatchesMatchDict]:
        json = response.json()
        matches = []
        competitions_id = {c["fotmob_id"] for c in COMPETITIONS.values()}
        for competition in json["leagues"]:
            if (competition_id := str(competition["id"])) in competitions_id:
                for match in competition["matches"]:
                    home_name = match["home"]["longName"]
                    away_name = match["away"]["longName"]
                    matches.append(
                        FotMobMatchesMatchDict(
                            id=str(match["id"]),
                            name=f"{home_name} vs {away_name}",
                            utc_time=match["status"]["utcTime"],
                            finished=match["status"]["finished"],
                            started=match["status"]["started"],
                            cancelled=match["status"]["cancelled"],
                            score=match["status"].get("scoreStr"),
                            competition=StatDict(
                                id=competition_id, name=competition["name"]
                            ),
                            home=StatDict(
                                id=str(match["home"]["id"]),
                                name=home_name,
                            ),
                            away=StatDict(
                                id=str(match["away"]["id"]),
                                name=away_name,
                            ),
                        )
                    )
        return matches


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

    def parse(self, response: httpx.Response) -> StatDict:
        json = response.json()
        home_team, away_team = json["header"]["teams"]
        home_name = home_team["name"]
        away_name = away_team["name"]
        return StatDict(id=self.id, name=f"{home_name} vs {away_name}")
