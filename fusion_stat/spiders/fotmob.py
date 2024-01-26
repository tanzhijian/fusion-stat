import httpx

from ..config import COMPETITIONS, POSITIONS
from ..scraper import Spider
from ..types import (
    base_types,
    competition_types,
    matches_types,
    player_types,
    staff_types,
    team_types,
)

BASE_URL = "https://www.fotmob.com/api"


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=BASE_URL + "/allLeagues")

    def parse(self, response: httpx.Response) -> list[base_types.StatDict]:
        json = response.json()
        competitions: list[base_types.StatDict] = []
        competitions_id = {
            params["fotmob_id"] for params in COMPETITIONS.values()
        }
        selection = json["popular"]
        for competition in selection:
            if (id := str(competition["id"])) in competitions_id:
                competitions.append(
                    base_types.StatDict(
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
    ) -> None:
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

    def parse(self, response: httpx.Response) -> competition_types.FotMobDict:
        json = response.json()
        name = json["details"]["name"]
        type_ = json["details"]["type"]
        season = json["details"]["selectedSeason"]
        country_code = json["details"]["country"]
        names = {name, json["details"]["shortName"]}

        teams = []
        for team in json["table"][0]["data"]["table"]["all"]:
            goals_for, goals_against = team["scoresStr"].split("-")
            teams.append(
                competition_types.FotMobTeamDict(
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
            home_score, away_score = _parse_score(
                match["status"].get("scoreStr")
            )
            matches.append(
                competition_types.FotMobMatchDict(
                    id=str(match["id"]),
                    name=f"{home_name} vs {away_name}",
                    utc_time=match["status"]["utcTime"],
                    finished=match["status"]["finished"],
                    started=match["status"]["started"],
                    cancelled=match["status"]["cancelled"],
                    competition=base_types.StatDict(id=self.id, name=name),
                    home=competition_types.FotMobMatchTeamDict(
                        id=str(match["home"]["id"]),
                        name=home_name,
                        score=home_score,
                    ),
                    away=competition_types.FotMobMatchTeamDict(
                        id=str(match["away"]["id"]),
                        name=away_name,
                        score=away_score,
                    ),
                )
            )

        return competition_types.FotMobDict(
            id=self.id,
            name=name,
            type=type_,
            season=season,
            country_code=country_code,
            names=names,
            teams=teams,
            matches=matches,
        )


class Team(Spider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/teams",
            params={"id": self.id},
        )

    def parse(self, response: httpx.Response) -> team_types.FotMobDict:
        json = response.json()
        id = str(json["details"]["id"])
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}
        country_code = json["details"]["country"]

        players = []
        squad = json["squad"]

        coach = squad[0][1][0]
        staff = team_types.FotMobStaffDict(
            id=str(coach["id"]),
            name=coach["name"],
            country=coach["cname"],
            country_code=coach["ccode"],
        )

        for role in squad[1:]:
            for player in role[1]:
                position = player.get("role")
                # 这里稍候移到 models 验证
                position = POSITIONS[position]
                players.append(
                    team_types.FotMobPlayerDict(
                        id=str(player["id"]),
                        name=player["name"],
                        country=player["cname"],
                        country_code=player["ccode"],
                        position=position,
                    )
                )

        return team_types.FotMobDict(
            id=id,
            name=name,
            names=names,
            country_code=country_code,
            staff=staff,
            players=players,
        )


class _Member(Spider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/playerData",
            params={"id": self.id},
        )


class Player(_Member):
    def __init__(self, *, id: str) -> None:
        super().__init__(id=id)

    def parse(self, response: httpx.Response) -> player_types.FotMobDict:
        json = response.json()
        name = json["name"]
        country = json["meta"]["personJSONLD"]["nationality"]["name"]
        position = json["positionDescription"]["primaryPosition"]["label"]
        return player_types.FotMobDict(
            id=self.id,
            name=name,
            country=country,
            position=position,
        )


class Staff(_Member):
    def __init__(self, *, id: str) -> None:
        super().__init__(id=id)

    def parse(self, response: httpx.Response) -> staff_types.FotMobDict:
        json = response.json()
        name = json["name"]
        return staff_types.FotMobDict(id=self.id, name=name)


class Matches(Spider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str) -> None:
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
    ) -> list[matches_types.FotMobMatchDict]:
        json = response.json()
        matches = []
        competitions_id = {c["fotmob_id"] for c in COMPETITIONS.values()}
        for competition in json["leagues"]:
            if (competition_id := str(competition["id"])) in competitions_id:
                for match in competition["matches"]:
                    home_name = match["home"]["longName"]
                    away_name = match["away"]["longName"]
                    home_score, away_score = _parse_score(
                        match["status"].get("scoreStr")
                    )
                    matches.append(
                        matches_types.FotMobMatchDict(
                            id=str(match["id"]),
                            name=f"{home_name} vs {away_name}",
                            utc_time=match["status"]["utcTime"],
                            finished=match["status"]["finished"],
                            started=match["status"]["started"],
                            cancelled=match["status"]["cancelled"],
                            competition=base_types.StatDict(
                                id=competition_id, name=competition["name"]
                            ),
                            home=matches_types.FotMobTeamDict(
                                id=str(match["home"]["id"]),
                                name=home_name,
                                score=home_score,
                            ),
                            away=matches_types.FotMobTeamDict(
                                id=str(match["away"]["id"]),
                                name=away_name,
                                score=away_score,
                            ),
                        )
                    )
        return matches


class Match(Spider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=BASE_URL + "/matchDetails",
            params={"matchId": self.id},
        )

    def parse(self, response: httpx.Response) -> base_types.StatDict:
        json = response.json()
        home_team, away_team = json["header"]["teams"]
        home_name = home_team["name"]
        away_name = away_team["name"]
        return base_types.StatDict(
            id=self.id, name=f"{home_name} vs {away_name}"
        )


def _parse_score(score_str: str | None) -> tuple[int | None, int | None]:
    """
    score_str: '3 - 2' or None
    """
    home_score, away_score = (
        [int(score) for score in score_str.split(" - ")]
        if score_str is not None
        else (None, None)
    )
    return home_score, away_score
