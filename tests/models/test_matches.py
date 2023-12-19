import httpx
import pytest

from fusion_stat import Matches
from fusion_stat.spiders import fbref, fotmob
from tests.utils import read_data


class TestMatches:
    @pytest.fixture(scope="class")
    def matches(self, client: httpx.AsyncClient) -> Matches:
        fotmob_data = read_data("fotmob", "matches?date=20230903.json")
        fbref_data = read_data("fbref", "matches_2023-09-03.html")

        fotmob_spider = fotmob.Matches(date="2023-09-03", client=client)
        fbref_spider = fbref.Matches(date="2023-09-03", client=client)

        return Matches(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_info(self, matches: Matches) -> None:
        info = matches.info
        match = info["matches"][0]
        assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
        assert match["score"] == "3 - 2"

    def test_index(self, matches: Matches) -> None:
        index = matches.index()
        assert len(index) == 18
        params = index[0]
        assert params["fotmob_id"] == "4193495"
        assert params["fbref_id"] == "f9436d32"
