import httpx
from parsel import Selector

from ...config import COMPETITIONS
from ...scraper import BaseItem, BaseSpider
from ...utils import get_element_text
from . import BASE_URL


class Item(BaseItem):
    ...


class Spider(BaseSpider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str) -> None:
        self.date = date

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.date}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> list[Item]:
        selector = Selector(response.text)
        matches: list[Item] = []

        competitions_id = "|".join(
            (
                comptition_params_dict["fbref_id"]
                for comptition_params_dict in COMPETITIONS.values()
            )
        )
        tables = selector.xpath(
            f"//table[re:test(@id, 'sched_.*_({competitions_id})\\b')]"
        )
        trs = tables.xpath("./tbody/tr")
        # 如果还没有进行的比赛会找不到对应节点
        for tr in trs:
            try:
                home_name = get_element_text(
                    tr.xpath('./td[@data-stat="home_team"]/a/text()')
                )
                away_name = get_element_text(
                    tr.xpath('./td[@data-stat="away_team"]/a/text()')
                )

                href = get_element_text(
                    tr.xpath('./td[@data-stat="score"]/a/@href')
                )
                id_ = href.split("/")[3]
                matches.append(
                    Item(
                        id=id_,
                        name=f"{home_name} vs {away_name}",
                    )
                )
            except ValueError:
                pass
        return matches
