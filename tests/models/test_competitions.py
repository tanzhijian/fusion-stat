import httpx
import pytest

from fusion_stat import Competitions
from fusion_stat.config import COMPETITIONS
from fusion_stat.spiders import fbref, fotmob, transfermarkt
from fusion_stat.types.base_types import StatDict
from tests.utils import read_data


class TestCompetitions:
    @pytest.fixture(scope="class")
    def competitions(self) -> Competitions:
        fotmob_data = read_data("fotmob", "allLeagues.json")
        fbref_data = read_data("fbref", "comps_.html")
        transfermarkt_data = read_data(
            "transfermarkt", "wettbewerbe_europa.html"
        )

        fotmob_spider = fotmob.Competitions()
        fbref_spider = fbref.Competitions()
        transfermarkt_spider = transfermarkt.Competitions()

        return Competitions(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
        )

    def test_info(self, competitions: Competitions) -> None:
        info = competitions.info
        assert info["count"] == 5
        assert info["names"][0] == "Premier League"

    def test_find_competition(self, competitions: Competitions) -> None:
        stats_dict = [StatDict(id="1", name="a")]
        result = competitions._find_competition("1", stats_dict)
        assert result["name"] == "a"

        with pytest.raises(ValueError):
            competitions._find_competition("a", stats_dict)

    def test_get_items(self, competitions: Competitions) -> None:
        items = competitions.get_items()
        competition = next(items)
        assert competition["id"] == "47"
        assert competition["fotmob"]["id"] == "47"
        assert competition["fbref"]["id"] == "9"
        assert competition["transfermarkt"]["id"] == "GB1"
        assert (
            competition["fotmob"]["name"]
            == competition["fbref"]["name"]
            == competition["transfermarkt"]["name"]
            == "Premier League"
        )

    def test_items(self, competitions: Competitions) -> None:
        items = competitions.items
        assert len(items) == 5

        for item in items:
            assert item["name"] in COMPETITIONS

    def test_get_params(self, competitions: Competitions) -> None:
        params = competitions.get_params()
        competition = next(params)
        assert competition["fbref_path_name"] == "Premier-League"
        assert competition["official_name"] == "Premier League"
        assert competition["transfermarkt_path_name"] == "premier-league"
        with pytest.raises(KeyError):
            assert competition["season"]
