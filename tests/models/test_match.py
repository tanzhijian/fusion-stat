import httpx
import pytest

from fusion_stat import Match
from fusion_stat.spiders import fbref, fotmob
from tests.utils import read_data


class TestMatch:
    @pytest.fixture(scope="class")
    def match(self) -> Match:
        fotmob_data = read_data("fotmob", "matchDetails?matchId=4193490.json")
        fbref_data = read_data("fbref", "matches_74125d47.html")

        fotmob_spider = fotmob.Match(id="4193490")
        fbref_spider = fbref.Match(id="74125d47")

        return Match(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_info(self, match: Match) -> None:
        assert match.fotmob["name"] == "Arsenal vs Manchester United"
        assert match.fbref["name"] == "Arsenal vs Manchester United"
