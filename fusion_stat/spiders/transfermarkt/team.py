import httpx
from parsel import Selector

from ...config import POSITIONS, fifa_members
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, HEADERS, convert_date_format, get_market_value


class PlayerItem(BaseItem):
    country_code: str
    position: str | None
    date_of_birth: str
    market_values: str
    path_name: str


class Item(BaseItem):
    market_values: str
    players: list[PlayerItem]


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
        path = f"/{self.path_name}/startseite/verein/{self.id}"
        if self.season is not None:
            path = f"{path}/saison_id/{self.season}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}", headers=HEADERS)

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/text()"))
        market_values = get_market_value(selector)

        player_trs = selector.xpath('//*[@id="yw1"]/table/tbody/tr')
        players = [self._parse_player(tr) for tr in player_trs]

        return Item(
            id=self.id,
            name=name,
            market_values=market_values,
            players=players,
        )

    def _parse_player(self, node: Selector) -> PlayerItem:
        tds = node.xpath("./td")

        a = tds[1].xpath("./table/tr[1]/td[2]/a")
        href_strs = get_element_text(a.xpath("./@href")).split("/")
        id_ = href_strs[-1]
        path_name = href_strs[-4]
        name = get_element_text(a.xpath("./text()"))

        position = get_element_text(tds[1].xpath("./table/tr[2]/td/text()"))
        position = POSITIONS[position]

        date_of_birth = get_element_text(tds[2].xpath("./text()"))
        date_of_birth = convert_date_format(date_of_birth)

        market_values = get_element_text(tds[-1].xpath("./a/text()"))

        country = get_element_text(tds[-2].xpath("./img[1]/@title"))
        country_code = fifa_members[(country)].code

        return PlayerItem(
            id=id_,
            name=name,
            date_of_birth=date_of_birth,
            market_values=market_values,
            path_name=path_name,
            country_code=country_code,
            position=position,
        )
