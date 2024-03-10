from parsel import Selector, SelectorList
from pydantic import BaseModel

from ...utils import get_element_text

BASE_URL = "https://fbref.com/en"


class ShootingItem(BaseModel):
    shots: int
    xg: float


def parse_shooting(
    tr: Selector | SelectorList[Selector],
) -> ShootingItem:
    shots = get_element_text(tr.xpath('./td[@data-stat="shots"]/text()'))
    xg = get_element_text(tr.xpath('./td[@data-stat="xg"]/text()'))
    return ShootingItem(
        shots=int(shots),
        xg=float(xg),
    )
