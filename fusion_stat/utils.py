import typing
from datetime import date

from parsel import Selector, SelectorList
from rapidfuzz import fuzz


def get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text


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


def fuzzy_similarity_mean(
    l1: list[str], l2: list[str], **kwargs: typing.Any
) -> float:
    # score_cutoff 参数会导致自定义 scorer 失效？
    scores = [fuzz.ratio(s1, s2) for s1, s2 in zip(l1, l2)]
    return sum(scores) / len(scores)


def current_season() -> tuple[int, int]:
    today = date.today()
    if today.month < 7:
        return today.year - 1, today.year
    return today.year, today.year + 1
