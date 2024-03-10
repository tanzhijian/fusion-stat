import httpx

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from . import BASE_URL, parse_score


class TeamItem(BaseItem):
    score: int | None


class Item(BaseItem):
    utc_time: str
    finished: bool
    started: bool
    cancelled: bool
    competition: BaseItem
    home: TeamItem
    away: TeamItem


class Matches(BaseSpider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str) -> None:
        self.date = date.replace("-", "")

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/matches",
            params={"date": self.date},
        )

    def parse(self, response: httpx.Response) -> list[Item]:
        json = response.json()
        matches = []
        competitions_id = {c["fotmob_id"] for c in COMPETITIONS.values()}
        for competition in json["leagues"]:
            if (competition_id := str(competition["id"])) in competitions_id:
                for match in competition["matches"]:
                    home_name = match["home"]["longName"]
                    away_name = match["away"]["longName"]
                    home_score, away_score = parse_score(
                        match["status"].get("scoreStr")
                    )
                    matches.append(
                        Item(
                            id=str(match["id"]),
                            name=f"{home_name} vs {away_name}",
                            utc_time=match["status"]["utcTime"],
                            finished=match["status"]["finished"],
                            started=match["status"]["started"],
                            cancelled=match["status"]["cancelled"],
                            competition=BaseItem(
                                id=competition_id, name=competition["name"]
                            ),
                            home=TeamItem(
                                id=str(match["home"]["id"]),
                                name=home_name,
                                score=home_score,
                            ),
                            away=TeamItem(
                                id=str(match["away"]["id"]),
                                name=away_name,
                                score=away_score,
                            ),
                        )
                    )
        return matches
