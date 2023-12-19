import httpx
import pytest

from fusion_stat import Competitions
from fusion_stat.spiders import fbref, fotmob
from tests.utils import read_data


class TestCompetitions:
    @pytest.fixture(scope="class")
    def competitions(self, client: httpx.AsyncClient) -> Competitions:
        fotmob_data = read_data("fotmob", "allLeagues.json")
        fbref_data = read_data("fbref", "comps_.html")

        fotmob_spider = fotmob.Competitions(client=client)
        fbref_spider = fbref.Competitions(client=client)

        return Competitions(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_index(self, competitions: Competitions) -> None:
        index = competitions.index()
        competition = index[0]
        assert competition["fbref_path_name"] == "Premier-League"
        assert competition["official_name"] == "Premier League"
        with pytest.raises(KeyError):
            assert competition["season"]
