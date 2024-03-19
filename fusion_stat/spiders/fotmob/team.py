import httpx

from ...config import POSITIONS
from ...scraper import BaseItem, BaseSpider
from ._common import BASE_URL


class _PersonItem(BaseItem):
    country_code: str
    country: str


class PlayerItem(_PersonItem):
    position: str | None


class StaffItem(_PersonItem):
    ...


class Item(BaseItem):
    names: set[str]
    country_code: str
    staff: StaffItem
    players: list[PlayerItem]


class Spider(BaseSpider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=f"{BASE_URL}/teams",
            params={"id": self.id},
        )

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        id_ = str(json["details"]["id"])
        name = json["details"]["name"]
        names = {name, json["details"]["shortName"]}
        country_code = json["details"]["country"]

        squad = json["squad"]

        coach = squad[0]["members"][0]
        staff = StaffItem(
            id=str(coach["id"]),
            name=coach["name"],
            country=coach["cname"],
            country_code=coach["ccode"],
        )

        players: list[PlayerItem] = []
        for group in squad[1:]:
            for player in group["members"]:
                position = player["role"]["fallback"]
                # 这里稍候移到 models 验证
                position = POSITIONS[position]
                players.append(
                    PlayerItem(
                        id=str(player["id"]),
                        name=player["name"],
                        country=player["cname"],
                        country_code=player["ccode"],
                        position=position,
                    )
                )

        return Item(
            id=id_,
            name=name,
            names=names,
            country_code=country_code,
            staff=staff,
            players=players,
        )
