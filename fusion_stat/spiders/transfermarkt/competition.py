import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, HEADERS, get_market_value


class TeamItem(BaseItem):
    market_values: str
    path_name: str


class Item(BaseItem):
    market_values: str
    player_average_market_value: str
    teams: list[TeamItem]


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str,
        season: int | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name
        self.season = season

    @property
    def request(self) -> httpx.Request:
        params = {}
        path = f"/{self.path_name}/startseite/wettbewerb/{self.id}"
        if self.season:
            path = f"{path}/plus/"
            params["saison_id"] = self.season
        return httpx.Request(
            "GET", url=f"{BASE_URL}{path}", params=params, headers=HEADERS
        )

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/text()"))
        player_average_market_value = get_element_text(
            selector.xpath(
                '//div[@class="data-header__details"]/ul[2]/li[1]/span/text()'
            )
        )
        market_values = get_market_value(selector)

        trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        teams = [self._parse_team(tr) for tr in trs]

        return Item(
            id=self.id,
            name=name,
            market_values=market_values,
            player_average_market_value=player_average_market_value,
            teams=teams,
        )

    def _parse_team(self, node: Selector) -> TeamItem:
        a = node.xpath("./td[7]/a")
        href_strs = get_element_text(a.xpath("./@href")).split("/")
        id_ = href_strs[-3]
        path_name = href_strs[-6]
        name = get_element_text(a.xpath("./@title"))
        market_values = get_element_text(a.xpath("./text()"))
        return TeamItem(
            id=id_,
            name=name,
            market_values=market_values,
            path_name=path_name,
        )
