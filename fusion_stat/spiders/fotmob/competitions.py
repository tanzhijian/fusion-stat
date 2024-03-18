import httpx
from rapidfuzz import process

from ...config import CompetitionsConfig
from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class Item(BaseItem):
    country_code: str


class Spider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=f"{BASE_URL}/allLeagues")

    def parse(self, response: httpx.Response) -> list[Item]:
        json = response.json()

        choices: list[tuple[str, str, str]] = []
        for country in json["countries"]:
            if (
                country_code := country["ccode"]
            ) in CompetitionsConfig.countries:
                for com in country["leagues"]:
                    choices.append((country_code, com["name"], str(com["id"])))

        competitions: list[Item] = []
        for query in CompetitionsConfig.data:
            result = process.extractOne(
                query,
                choices,
                processor=lambda x: x[1],
            )[0]
            competitions.append(
                Item(
                    id=result[2],
                    name=query[1],
                    country_code=result[0],
                )
            )

        return competitions
