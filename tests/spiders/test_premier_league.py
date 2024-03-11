import httpx
import pytest

from fusion_stat.spiders import official
from fusion_stat.spiders.official.competitions import PremierLeagueSpider
from tests.utils import read_data


class testCompetitions:
    @pytest.fixture(scope="class")
    def spider(self) -> PremierLeagueSpider:
        return PremierLeagueSpider()

    def test_request(self, spider: PremierLeagueSpider) -> None:
        assert (
            spider.request.headers["Origin"] == "https://www.premierleague.com"
        )

    def test_parse_and_index(self, spider: PremierLeagueSpider) -> None:
        data = read_data(
            "premier_league", "competitions?page=0&pageSize=1000&detail=2.json"
        )
        response = httpx.Response(200, json=data)
        coms = spider.parse(response)
        assert coms[0].name == "Premier League"
        assert coms[0].seasons[0].name == "2023/24"

        index = spider.index(coms)
        assert index["Premier League"]["2023"] == "578"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> official.competition.Spider:
        return official.competition.Spider(name="Premier League", season=2023)

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
        assert com.id == "Premier League 2023"
        assert com.name == "Premier League"
        team = com.teams[0]
        assert team.name == "Arsenal"
        assert team.country_code == "ENG"
        assert (
            team.logo
            == "https://resources.premierleague.com/premierleague/badges/rb/t3.svg"
        )
