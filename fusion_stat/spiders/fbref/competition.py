import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from ._common import BASE_URL, ShootingItem, parse_shooting


class TeamItem(BaseItem):
    path_name: str
    names: set[str]
    shooting: ShootingItem


class Item(BaseItem):
    teams: list[TeamItem]


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
            path = f"/comps/{self.id}/{self.season}"
            if self.path_name:
                path = f"{path}/{self.season}-{self.path_name}-Stats"
        else:
            path = f"/comps/{self.id}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/text()"))
        name = " ".join(h1.split(" ")[1:-1])

        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        teams = [self._parse_team(tr) for tr in trs]
        return Item(
            id=self.id,
            name=name,
            teams=teams,
        )

    def _parse_team(self, node: Selector) -> TeamItem:
        href_strs = get_element_text(node.xpath("./th/a/@href")).split("/")
        path_name_strs = href_strs[-1].split("-")[:-1]
        path_name = "-".join(path_name_strs)
        name = " ".join(path_name_strs)
        name_2 = get_element_text(node.xpath("./th/a/text()"))
        shooting = parse_shooting(node)
        return TeamItem(
            id=href_strs[3],
            name=name_2,
            names={name, name_2},
            path_name=path_name,
            shooting=shooting,
        )
