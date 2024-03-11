import httpx

from ...scraper import BaseItem, BaseSpider
from ._common import Headers


class Item(BaseItem):
    seasons: list[BaseItem]


class PremierLeagueSpider(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=(
                "https://footballapi.pulselive.com/football"
                "/competitions?page=0&pageSize=1000&detail=2"
            ),
            headers=Headers.premier_league,
        )

    def parse(self, response: httpx.Response) -> list[Item]:
        json = response.json()
        # only pl
        pl = json["content"][1]
        seasons = [
            BaseItem(
                id=str(int(season["id"])),
                name=season["label"],
            )
            for season in pl["compSeasons"]
        ]
        return [
            Item(
                id=pl["description"],
                name=pl["description"],
                seasons=seasons,
            ),
        ]

    def index(
        self,
        competitions: list[Item],
    ) -> dict[str, dict[str, str]]:
        """Generate COMPETITIONS_SEASON_INDEX"""
        competitions_seasons_index = {}
        for competition in competitions:
            seasons_index = {}
            for season in competition.seasons:
                seasons_index[season.name.split("/")[0]] = season.id
            competitions_seasons_index[competition.name] = seasons_index
        return competitions_seasons_index
