import httpx
import pytest

from fusion_stat import Competitions
from fusion_stat.models.base import StatDict
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

    def test_find_competition_by_id(self, competitions: Competitions) -> None:
        stats_dict = (StatDict(id="1", name="a"),)
        result = competitions._find_competition_by_id(stats_dict, "1")
        assert result["name"] == "a"

        with pytest.raises(ValueError):
            competitions._find_competition_by_id(stats_dict, "a")

    def test_items(self, competitions: Competitions) -> None:
        items = competitions.items
        assert len(items) == 5
        competition = items[0]
        assert competition["id"] == "47"
        assert competition["fotmob"]["id"] == "47"
        assert competition["fbref"]["id"] == "9"
        assert (
            competition["fotmob"]["name"]
            == competition["fbref"]["name"]
            == "Premier League"
        )

    def test_get_params(self, competitions: Competitions) -> None:
        params = competitions.get_params()
        assert len(params) == 5
        competition = params[0]
        assert competition["fbref_path_name"] == "Premier-League"
        assert competition["official_name"] == "Premier League"
        with pytest.raises(KeyError):
            assert competition["season"]
