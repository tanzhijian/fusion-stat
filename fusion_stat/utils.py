import typing
from datetime import date, datetime

from parsel import Selector, SelectorList
from rapidfuzz import fuzz, process


def get_element_text(selector_list: Selector | SelectorList[Selector]) -> str:
    if not (text := "".join(selector_list.getall())):
        raise ValueError("tag not found")
    return text.strip()


def mean_scorer(l1: list[str], l2: list[str], **kwargs: typing.Any) -> float:
    # score_cutoff 参数会导致自定义 scorer 失效？
    scores = [fuzz.ratio(s1, s2) for s1, s2 in zip(l1, l2)]
    return sum(scores) / len(scores)


T = typing.TypeVar("T")


def match(
    tasks: typing.Sequence[typing.Sequence[T]],
    *,
    processor: typing.Callable[[T], list[str]],
    scorer: typing.Callable[..., int | float] = fuzz.WRatio,
    score_cutoff: int | float | None = None,
) -> list[list[T]]:
    if len(tasks) < 2:
        raise ValueError("at least two tasks are required")

    results: list[list[T]] = []
    for query in tasks[0]:
        row: list[T] = []
        for choices in tasks[1:]:
            result = process.extractOne(
                query,
                choices,
                processor=processor,
                scorer=scorer,
                score_cutoff=score_cutoff,
            )
            row.append(result[0])
        results.append(row)
    return results


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
