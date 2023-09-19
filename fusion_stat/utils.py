import typing

from rapidfuzz import process


def most_similar(
    name: str,
    names: set[str] | list[str] | tuple[str, ...],
    **kwargs: typing.Any
) -> str | None:
    result = process.extractOne(
        name,
        names,
        **kwargs,
    )
    if result:
        return result[0]
    return None


def is_in(name: str, names: set[str] | list[str] | tuple[str, ...]) -> bool:
    result = most_similar(name, names, score_cutoff=80)
    return bool(result)
