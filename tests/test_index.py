from fusion_stat.models import Competition, Competitions
from fusion_stat._index import get_competitions_index


def test_get_competitions_index() -> None:
    fotmob = [Competition(id="87", name="LaLiga")]
    fbref = [Competition(id="12", name="La Liga")]
    coms = Competitions(fotmob=fotmob, fbref=fbref)

    index = get_competitions_index(coms)
    assert index["LL"]["fotmob"]["id"] == "87"
