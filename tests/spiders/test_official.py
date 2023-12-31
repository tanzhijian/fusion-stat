import typing

import httpx
import pytest

from fusion_stat.config import COMPETITIONS
from fusion_stat.spiders.official import Competition
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Premier League", client=client)

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
        assert com["name"] == "Premier League"
        team = com["teams"][0]
        assert team["name"] == "Arsenal"
        assert (
            team["logo"]
            == "https://resources.premierleague.com/premierleague/badges/rb/t3.svg"
        )


def test_select_competition(client: httpx.AsyncClient) -> None:
    for name in COMPETITIONS:
        spider = Competition(name=name, season=2023, client=client)
        assert spider.name == name

    with pytest.raises(KeyError):
        spider = Competition(name="Foo", season=2023, client=client)
        assert spider.name == "Foo"
