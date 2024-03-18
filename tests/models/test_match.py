import httpx
import pytest

from fusion_stat import Match
from fusion_stat.spiders import fotmob
from tests.utils import read_data


class TestMatch:
    @pytest.fixture(scope="class")
    def match(self) -> Match:
        fotmob_data = read_data("fotmob", "matchDetails?matchId=4193490.json")

        fotmob_spider = fotmob.match.Spider(id="4193490")

        return Match(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
        )
