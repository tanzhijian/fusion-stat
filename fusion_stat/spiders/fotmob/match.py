import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/matchDetails",
            params={"matchId": self.id},
        )

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        home_team, away_team = json["header"]["teams"]
        home_name = home_team["name"]
        away_name = away_team["name"]
        return Item(id=self.id, name=f"{home_name} vs {away_name}")
