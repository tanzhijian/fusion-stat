import pytest
from parsel import Selector

from fusion_stat.utils import (
    concatenate_strings,
    current_season,
    fuzzy_similarity_mean,
    get_element_text,
)


def test_get_element_text_non_empty() -> None:
    html = "<div>Test</div>"
    selector = Selector(text=html)
    result = get_element_text(selector.xpath("//div/text()"))
    assert result == "Test"


def test_get_element_text_empty() -> None:
    html = "<div></div>"
    selector = Selector(text=html)
    with pytest.raises(ValueError):
        get_element_text(selector.xpath("//div/text()"))


def test_fuzzy_similarity_mean() -> None:
    l1 = ["Gabriel", "BRA", "DF"]
    l2 = ["Gabriel Dos Santos", "BRA", "DF"]
    score = fuzzy_similarity_mean(l1, l2)
    assert score > 80


def test_current_season() -> None:
    start, end = current_season()
    assert end - start == 1


def test_concatenate_strings() -> None:
    assert concatenate_strings("foo", "bar") == "foo_bar"
    assert concatenate_strings("", "bar") == "bar"
    assert concatenate_strings("foo bar", "foo") == "foo_bar_foo"
