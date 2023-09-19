from fusion_stat.utils import most_similar, is_in


def test_most_similar() -> None:
    result = most_similar("a", ("ab", "bc"))
    assert result == "ab"


def test_is_in() -> None:
    names = {
        "Premier League",
        "LaLiga",
        "Bundesliga",
    }
    assert is_in("La Liga", names)
    assert not is_in("Super League", names)
