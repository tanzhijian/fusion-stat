import typing
from parsel import Selector, SelectorList
from rapidfuzz import fuzz

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


def unpack_params(
    params: Params | dict[str, str]
) -> dict[str, dict[str, str]]:
    if isinstance(params, dict):
        params = Params(**params)

    fotmob = {"id": params.fotmob_id}
    fbref = {"id": params.fbref_id}
    if params.fbref_path_name:
        fbref["path_name"] = params.fbref_path_name
    return {"fotmob": fotmob, "fbref": fbref}


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
