import httpx

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=f"{BASE_URL}/allLeagues")

    def parse(self, response: httpx.Response) -> list[Item]:
        json = response.json()
        competitions: list[Item] = []
        competitions_id = {
            params["fotmob_id"] for params in COMPETITIONS.values()
        }
        selection = json["popular"]
        for competition in selection:
            if (id_ := str(competition["id"])) in competitions_id:
                competitions.append(Item(id=id_, name=competition["name"]))
        return competitions
