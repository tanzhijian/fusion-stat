import pytest
from pydantic import ValidationError

from fusion_stat.utils import (
    unpack_params,
    sort_table_key,
    fuzzy_similarity_mean,
    current_season,
)
from fusion_stat.models import Params


def test_unpack_params() -> None:
    params = unpack_params(
        Params(
            fotmob_id="47",
            fbref_id="9",
            fbref_path_name="Premier-League",
        )
    )
    assert params["fotmob"]["id"] == "47"

    params = unpack_params(
        {
            "fotmob_id": "47",
            "fbref_id": "9",
            "fbref_path_name": "Premier-League",
        }
    )
    assert params["fotmob"]["id"] == "47"

    with pytest.raises(ValidationError):
        params = unpack_params({"foo": "bar"})


def test_sort_table_key() -> None:
    team = {
        "name": "A",
        "points": 20,
        "goals_for": 20,
        "goals_against": 10,
    }
    key = sort_table_key(team)
    assert key[0] == -20


def test_fuzzy_similarity_mean() -> None:
    l1 = ["Gabriel", "BRA", "DF"]
    l2 = ["Gabriel Dos Santos", "BRA", "DF"]
    score = fuzzy_similarity_mean(l1, l2)
    assert score > 80


def test_current_season() -> None:
    start, end = current_season()
    assert end - start == 1
