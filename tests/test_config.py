from fusion_stat.config import COMPETITIONS_INDEX


def test_competitions_index() -> None:
    assert COMPETITIONS_INDEX["PL"]["fotmob"]["id"] == "47"
