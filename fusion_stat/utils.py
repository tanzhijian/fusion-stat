import typing
from datetime import date

from parsel import Selector, SelectorList
from rapidfuzz import fuzz


def get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text


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
