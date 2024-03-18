import httpx
import pytest

from fusion_stat.config import CompetitionsConfig
from fusion_stat.spiders import official
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> official.competition.Spider:
        return official.competition.Spider(name="Premier League")

    def test_request(self, spider: official.competition.Spider) -> None:
        assert (
            spider.request.url
            == "https://footballapi.pulselive.com/football/teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0"
        )
        assert (
            spider.request.headers["Origin"] == "https://www.premierleague.com"
        )

    def test_parse(self, spider: official.competition.Spider) -> None:
        data = read_data(
            "premier_league",
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json",
        )
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.name == "Premier League"


def test_select_competition() -> None:
    for _, name in CompetitionsConfig.data:
        spider = official.competition.Spider(name=name, season=2023)
        assert spider.name == name

    with pytest.raises(KeyError):
        spider = official.competition.Spider(name="Foo", season=2023)
        assert spider.name == "Foo"
