from fusion_stat.utils import (
    current_season,
    fuzzy_similarity_mean,
    sort_table_key,
)


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
