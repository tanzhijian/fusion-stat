import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, ShootingItem, parse_shooting


class PlayerItem(BaseItem):
    names: set[str]
    path_name: str
    country_code: str
    position: str | None
    shooting: ShootingItem


class Item(BaseItem):
    names: set[str]
    shooting: ShootingItem
    players: list[PlayerItem]


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: int | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name
        if season is None:
            self.season = season
        else:
            self.season = f"{season}-{season + 1}"

    @property
    def request(self) -> httpx.Request:
        if self.season:
            path = f"/squads/{self.id}/{self.season}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"
        else:
            path = f"/squads/{self.id}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/span[1]/text()"))
        name = " ".join(h1.split(" ")[1:-1])

        standard_stats_table = selector.xpath(
            '//table[starts-with(@id,"stats_standard_")]'
        )
        shooting_table = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]'
        )
        shooting = parse_shooting(shooting_table.xpath("./tfoot/tr[1]"))

        players_shooting_index: dict[str, ShootingItem] = {}
        for tr in shooting_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            player_id = href.split("/")[3]
            player_shooting = parse_shooting(tr)
            players_shooting_index[player_id] = player_shooting

        players: list[PlayerItem] = []
        for tr in standard_stats_table.xpath("./tbody/tr"):
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            player_path_name = href_strs[-1]
            player_id = href_strs[3]
            player_name = get_element_text(tr.xpath("./th/a/text()"))
            country_code = get_element_text(
                tr.xpath('./td[@data-stat="nationality"]/a/@href')
            ).split("/")[3]

            position = get_element_text(
                tr.xpath('./td[@data-stat="position"]/text()')
            )
            try:
                player_shooting = players_shooting_index[player_id]
            except KeyError:
                player_shooting = ShootingItem(shots=0, xg=0)
            players.append(
                PlayerItem(
                    id=player_id,
                    name=player_name,
                    names={player_name, " ".join(player_path_name.split("-"))},
                    path_name=player_path_name,
                    country_code=country_code,
                    position=position,
                    shooting=player_shooting,
                )
            )

        return Item(
            id=self.id,
            name=name,
            names={name},
            shooting=shooting,
            players=players,
        )
