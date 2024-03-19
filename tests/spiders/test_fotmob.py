from functools import partial
from urllib.parse import unquote

import httpx
import pytest

from fusion_stat.spiders import fotmob
from fusion_stat.spiders.fotmob._common import parse_score
from tests.utils import read_data

read_test_data = partial(read_data, "fotmob")


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.competitions.Spider:
        return fotmob.competitions.Spider()

    def test_request(self, spider: fotmob.competitions.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/allLeagues"

    def test_parse(self, spider: fotmob.competitions.Spider) -> None:
        data = read_test_data("allLeagues.json")
        response = httpx.Response(200, json=data)
        coms = spider.parse(response)
        assert len(coms) == 5

        com = coms[0]
        assert com.id == "47"
        assert com.name == "Premier League"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.competition.Spider:
        return fotmob.competition.Spider(id="47")

    def test_request(self, spider: fotmob.competition.Spider) -> None:
        assert spider.request.url == "https://www.fotmob.com/api/leagues?id=47"

    def test_request_include_season(
        self, spider: fotmob.competition.Spider
    ) -> None:
        spider = fotmob.competition.Spider(id="47", season=2022)
        assert (
            spider.request.url
            == "https://www.fotmob.com/api/leagues?id=47&season=2022%2F2023"
        )
        assert unquote(str(spider.request.url)) == (
            "https://www.fotmob.com/api/leagues?id=47&season=2022/2023"
        )

    def test_parse(self, spider: fotmob.competition.Spider) -> None:
        data = read_test_data("leagues?id=47.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.id == "47"
        assert com.name == "Premier League"
        assert "Premier League" in com.names
        assert com.type == "league"
        assert com.season == "2023/2024"
        assert com.country_code == "ENG"

        assert len(com.teams) == 20
        team = com.teams[0]
        assert team.id == "8456"
        assert team.name == "Manchester City"
        assert "Man City" in team.names
        assert team.played == 4
        assert team.wins == 4
        assert team.draws == 0
        assert team.losses == 0
        assert team.goals_for == 11
        assert team.goals_against == 2
        assert team.points == 12

        assert len(com.matches) == 380
        match = com.matches[0]
        assert match.id == "4193450"
        assert match.name == "Burnley vs Manchester City"
        assert match.utc_time == "2023-08-11T19:00:00.000Z"
        assert match.finished
        assert match.started
        assert not match.cancelled
        home = match.home
        assert home.id == "8191"
        assert home.name == "Burnley"
        assert home.score == 0
        away = match.away
        assert away.id == "8456"
        assert away.name == "Manchester City"
        assert away.score == 3


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.team.Spider:
        return fotmob.team.Spider(id="9825")

    def test_request(self, spider: fotmob.team.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/teams?id=9825"

    def test_parse(self, spider: fotmob.team.Spider) -> None:
        data = read_test_data("teams?id=9825.json")
        response = httpx.Response(200, json=data)
        team = spider.parse(response)
        assert team.id == "9825"
        assert team.name == "Arsenal"
        assert "Arsenal" in team.names
        assert team.country_code == "ENG"

        staff = team.staff
        assert staff.id == "24011"
        assert staff.name == "Mikel Arteta"
        assert staff.country == "Spain"
        assert staff.country_code == "ESP"

        assert len(team.players) == 26
        player = team.players[0]
        assert player.id == "562727"
        assert player.name == "David Raya"
        assert player.position == "GK"
        assert player.country == "Spain"
        assert player.country_code == "ESP"


class TestPlayer:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.player.Spider:
        return fotmob.player.Spider(id="961995")

    def test_request(self, spider: fotmob.player.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/playerData?id=961995"

    def test_parse(self, spider: fotmob.player.Spider) -> None:
        data = read_test_data("playerData?id=961995.json")
        response = httpx.Response(200, json=data)
        player = spider.parse(response)
        assert player.id == "961995"
        assert player.name == "Bukayo Saka"
        assert player.country == "England"
        assert player.position == "Right Winger"


class TestStaff:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.staff.Spider:
        return fotmob.staff.Spider(id="961995")

    def test_request(self, spider: fotmob.staff.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/playerData?id=961995"


class TestMatches:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.matches.Spider:
        return fotmob.matches.Spider(date="2023-09-03")

    def test_request(self, spider: fotmob.matches.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/matches?date=20230903"

    def test_parse(self, spider: fotmob.matches.Spider) -> None:
        data = read_test_data("matches?date=20230903.json")
        response = httpx.Response(200, json=data)
        matches = spider.parse(response)
        assert len(matches) == 19
        match = matches[0]
        assert match.id == "4193495"
        assert match.name == "Crystal Palace vs Wolverhampton Wanderers"
        assert match.utc_time == "2023-09-03T13:00:00.000Z"
        assert match.finished
        assert match.started
        assert not match.cancelled
        home = match.home
        assert home.id == "9826"
        assert home.name == "Crystal Palace"
        assert home.score == 3
        away = match.away
        assert away.id == "8602"
        assert away.name == "Wolverhampton Wanderers"
        assert away.score == 2


class TestMatch:
    @pytest.fixture(scope="class")
    def spider(self) -> fotmob.match.Spider:
        return fotmob.match.Spider(id="4193490")

    def test_request(self, spider: fotmob.match.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/matchDetails?matchId=4193490"

    def test_parse(self, spider: fotmob.match.Spider) -> None:
        data = read_test_data("matchDetails?matchId=4193490.json")
        response = httpx.Response(200, json=data)
        match = spider.parse(response)
        assert match.id == "4193490"
        assert match.name == "Arsenal vs Manchester United"


@pytest.mark.parametrize(
    "score, expected_home_score, expected_away_score",
    [("3 - 2", 3, 2), (None, None, None)],
)
def test_parse_score(
    score: str | None,
    expected_home_score: int | None,
    expected_away_score: int | None,
) -> None:
    home_score, away_score = parse_score(score)
    assert home_score == expected_home_score
    assert away_score == expected_away_score
