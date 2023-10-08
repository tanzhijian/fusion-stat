import typing
from parsel import Selector, SelectorList

from .models import Params, FBrefShooting


def get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text


def parse_fbref_shooting(
    tr: Selector | SelectorList[Selector],
) -> FBrefShooting:
    shots = get_element_text(tr.xpath('./td[@data-stat="shots"]/text()'))
    xg = get_element_text(tr.xpath('./td[@data-stat="xg"]/text()'))
    return FBrefShooting(
        shots=float(shots),
        xg=float(xg),
    )


def unpack_params(params: Params | dict[str, str]) -> Params:
    if isinstance(params, dict):
        return Params(**params)
    return params


def sort_table_key(team: dict[str, typing.Any]) -> tuple[typing.Any, ...]:
    """1. 首先按照积分降序排序，积分高的排在前面
    2. 如果两个或多个球队的积分相同，则根据以下规则进行排序：
        1. 净胜球降序排序
        2. 如果净胜球也相同，则根据进球数降序排序
        3. 如果进球数也相同，则根据球队的名称（字母顺序）升序排序
    """
    goal_difference = team["goals_for"] - team["goals_against"]
    return (
        -team["points"],
        -goal_difference,
        -team["goals_for"],
        team["name"],
    )
