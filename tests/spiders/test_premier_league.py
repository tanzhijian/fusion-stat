import typing

import httpx
import pytest

from fusion_stat.spiders.premier_league import Competition, Competitions
from tests.utils import read_data


class testCompetitions:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions()

    def test_request(self, spider: Competitions) -> None:
        assert (
            spider.request.headers["Origin"] == "https://www.premierleague.com"
        )

    def test_parse_and_index(self, spider: Competitions) -> None:
        data = read_data(
            "premier_league", "competitions?page=0&pageSize=1000&detail=2.json"
        )
        response = httpx.Response(200, json=data)
        coms = spider.parse(response)
        assert coms[0]["name"] == "Premier League"
        assert coms[0]["seasons"][0]["name"] == "2023/24"

        index = spider.index(coms)
        assert index["Premier League"]["2023"] == "578"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Premier League", season=2023)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://footballapi.pulselive.com/football/teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0"
        )
        assert (
            spider.request.headers["Origin"] == "https://www.premierleague.com"
        )

    def test_parse(self, spider: Competition) -> None:
        data = read_data(
            "premier_league",
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json",
        )
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com["id"] == "Premier League 2023"
        assert com["name"] == "Premier League"
        team = com["teams"][0]
        assert team["name"] == "Arsenal"
        assert team["country_code"] == "ENG"
        assert (
            team["logo"]
            == "https://resources.premierleague.com/premierleague/badges/rb/t3.svg"
        )
