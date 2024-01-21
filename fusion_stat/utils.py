import typing
from datetime import date, datetime

from parsel import Selector, SelectorList
from rapidfuzz import fuzz


def get_element_text(selector_list: Selector | SelectorList[Selector]) -> str:
    if not (text := "".join(selector_list.getall())):
        raise ValueError("tag not found")
    return text.strip()


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


def concatenate_strings(*args: str) -> str:
    return "_".join(arg.replace(" ", "_") for arg in args if arg)


def format_date(utc_time: str) -> str:
    """
    "2024-01-07T11:30:00.000Z" => "2024-01-07"
    """
    dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d")
