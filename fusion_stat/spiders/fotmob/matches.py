import typing

import httpx
from rapidfuzz import process

from ...config import COMPETITIONS_SCORE_CUTOFF, CompetitionsConfig
from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL, parse_score


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


class Spider(BaseSpider):
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

        choices: list[tuple[str, str, str, typing.Any]] = []
        for com in json["leagues"]:
            if (country_code := com["ccode"]) in CompetitionsConfig.countries:
                choices.append(
                    (country_code, com["name"], str(com["id"]), com["matches"])
                )

        matches: list[Item] = []
        for query in CompetitionsConfig.data:
            # 暂时用 .replace(" ", "") 消除了
            # 'Premier League', 'Premier League U18'
            # 所引发的匹配错误，后续会更新更好的方法
            result = process.extractOne(
                query,
                choices,
                processor=lambda x: x[1].replace(" ", ""),
                score_cutoff=COMPETITIONS_SCORE_CUTOFF,
            )
            if result is not None:
                choice = result[0]
                for node in choice[3]:
                    match = self._parse_match(
                        choice[0], choice[1], choice[2], node
                    )
                    matches.append(match)
        return matches

    def _parse_match(
        self,
        competition_country_code: str,
        competition_name: str,
        competition_id: str,
        node: typing.Any,
    ) -> Item:
        # country_code 字段暂时没用上
        home_name = node["home"]["longName"]
        away_name = node["away"]["longName"]
        home_score, away_score = parse_score(node["status"].get("scoreStr"))
        return Item(
            id=str(node["id"]),
            name=f"{home_name} vs {away_name}",
            utc_time=node["status"]["utcTime"],
            finished=node["status"]["finished"],
            started=node["status"]["started"],
            cancelled=node["status"]["cancelled"],
            competition=BaseItem(id=competition_id, name=competition_name),
            home=TeamItem(
                id=str(node["home"]["id"]),
                name=home_name,
                score=home_score,
            ),
            away=TeamItem(
                id=str(node["away"]["id"]),
                name=away_name,
                score=away_score,
            ),
        )
