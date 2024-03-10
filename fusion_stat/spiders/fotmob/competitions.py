import httpx

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from . import BASE_URL


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=f"{BASE_URL}/allLeagues")

    def parse(self, response: httpx.Response) -> list[BaseItem]:
        json = response.json()
        competitions: list[BaseItem] = []
        competitions_id = {
            params["fotmob_id"] for params in COMPETITIONS.values()
        }
        selection = json["popular"]
        for competition in selection:
            if (id_ := str(competition["id"])) in competitions_id:
                competitions.append(
                    BaseItem(
                        id=id_,
                        name=competition["name"],
                    )
                )
        return competitions
