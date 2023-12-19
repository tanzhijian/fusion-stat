import httpx
import pytest

from fusion_stat import Match
from fusion_stat.spiders.fbref import Match as FBrefMatch
from fusion_stat.spiders.fotmob import Match as FotMobMatch
from tests.utils import read_data


class TestMatch:
    @pytest.fixture(scope="class")
    def match(self, client: httpx.AsyncClient) -> Match:
        fotmob_data = read_data("fotmob", "matchDetails?matchId=4193490.json")
        fbref_data = read_data("fbref", "matches_74125d47.html")

        fotmob = FotMobMatch(id="4193490", client=client)
        fbref = FBrefMatch(id="74125d47", client=client)

        return Match(
            fotmob=fotmob.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_info(self, match: Match) -> None:
        assert match.fotmob.name == "Arsenal vs Manchester United"
        assert match.fbref.name == "Arsenal vs Manchester United"
