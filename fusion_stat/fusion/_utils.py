from parsel import Selector, SelectorList
from fusion_stat.models import FBrefShootingModel


def get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text


def parse_fbref_shooting(
    tr: Selector | SelectorList[Selector],
) -> FBrefShootingModel:
    shots = get_element_text(tr.xpath('./td[@data-stat="shots"]/text()'))
    xg = get_element_text(tr.xpath('./td[@data-stat="xg"]/text()'))
    return FBrefShootingModel(
        shots=float(shots),
        xg=float(xg),
    )
