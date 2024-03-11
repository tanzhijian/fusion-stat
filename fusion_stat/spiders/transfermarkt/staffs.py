import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL, HEADERS


class Item(BaseItem):
    position: str
    path_name: str


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        season: int | None = None,
    ) -> None:
        self.id = id
        self.season = season

    @property
    def request(self) -> httpx.Request:
        params = {}
        path = f"/ceapi/staff/team/{self.id}/"
        if self.season:
            params["saison_id"] = self.season
        return httpx.Request(
            "GET", url=f"{BASE_URL}{path}", params=params, headers=HEADERS
        )

    def parse(self, response: httpx.Response) -> list[Item]:
        json = response.json()
        return [
            Item(
                id=staff["id"],
                name=staff["name"],
                position=staff["position"],
                path_name=staff["profileUrl"].split("/")[1],
            )
            for staff in json["staff"]
        ]
