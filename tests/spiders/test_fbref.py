import typing
from functools import partial

import httpx
import pytest

from fusion_stat.spiders.fbref import (
    Competition,
    Competitions,
    Match,
    Matches,
    Player,
    Team,
)
from tests.utils import read_data

read_test_data = partial(read_data, "fbref")


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions()

    def test_request(self, spider: Competitions) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/comps/"

    def test_parse(self, spider: Competitions) -> None:
        text = read_test_data("comps_.html")
        response = httpx.Response(200, text=text)
        coms = spider.parse(response)
        assert len(coms) == 5
        com = coms[0]
        assert com["id"] == "9"
        assert com["name"] == "Premier League"
        assert com["path_name"] == "Premier-League"
        # 目前的赛事清单测试不到 INT
        assert com["country_code"] == "ENG"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="9", path_name="Premier-League")

    def test_request(self, spider: Competition) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/comps/9/Premier-League-Stats"

    def test_request_path_name_and_season(self) -> None:
        for url, spider in zip(
            (
                "https://fbref.com/en/comps/9",
                "https://fbref.com/en/comps/9/2022-2023",
                (
                    "https://fbref.com/en/comps/9/2022-2023/"
                    "2022-2023-Premier-League-Stats"
                ),
            ),
            (
                Competition(id="9"),
                Competition(id="9", season=2022),
                Competition(id="9", season=2022, path_name="Premier-League"),
            ),
        ):
            assert url == spider.request.url

    def test_parse(self, spider: Competition) -> None:
        text = read_test_data("comps_9_Premier-League-Stats.html")
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com["id"] == "9"
        assert com["name"] == "Premier League"

        assert len(com["teams"]) == 20
        ars = com["teams"][0]
        assert ars["id"] == "18bb7c10"
        assert ars["name"] == "Arsenal"
        assert ars["path_name"] == "Arsenal"
        assert "Arsenal" in ars["names"]
        ast = com["teams"][1]
        assert ast["name"] == "Aston Villa"
        assert ast["path_name"] == "Aston-Villa"


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Team, typing.Any, None]:
        yield Team(id="18bb7c10", path_name="Arsenal")

    def test_request(self, spider: Team) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"

    def test_request_path_name_and_season(self) -> None:
        for url, spider in zip(
            (
                "https://fbref.com/en/squads/18bb7c10",
                "https://fbref.com/en/squads/18bb7c10/2022-2023",
                "https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats",
            ),
            (
                Team(id="18bb7c10"),
                Team(id="18bb7c10", season=2022),
                Team(id="18bb7c10", path_name="Arsenal", season=2022),
            ),
        ):
            assert url == spider.request.url

    def test_parse(self, spider: Team) -> None:
        text = read_test_data("squads_18bb7c10_Arsenal-Stats.html")
        response = httpx.Response(200, text=text)
        team = spider.parse(response)
        assert team["id"] == "18bb7c10"
        assert team["name"] == "Arsenal"
        assert "Arsenal" in team["names"]

        shooting = team["shooting"]
        assert shooting["shots"] == 63
        assert int(shooting["xg"] * 10) == int(8.3 * 10)

        assert len(team["players"]) == 23
        player = team["players"][4]
        assert player["id"] == "bc7dc64d"
        assert player["name"] == "Bukayo Saka"
        assert "Bukayo Saka" in player["names"]
        assert player["path_name"] == "Bukayo-Saka"
        assert player["position"] == "FW"
        assert player["country_code"] == "ENG"
        player_shooting = player["shooting"]
        assert player_shooting["shots"] == 11
        assert int(player_shooting["xg"] * 10) == int(2.2 * 10)


class TestPlayer:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Player, typing.Any, None]:
        yield Player(id="bc7dc64d", path_name="Bukayo-Saka")

    def test_request(self, spider: Player) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/players/bc7dc64d/Bukayo-Saka"

    def test_request_exclude_path_name(self) -> None:
        spider = Player(id="bc7dc64d")
        assert spider.request.url == "https://fbref.com/en/players/bc7dc64d/"

    def test_parse(self, spider: Player) -> None:
        text = read_test_data("players_bc7dc64d_Bukayo-Saka.html")
        response = httpx.Response(200, text=text)
        player = spider.parse(response)
        assert player["id"] == "bc7dc64d"
        assert player["name"] == "Bukayo Saka"
        player_shooting = player["shooting"]
        assert player_shooting["shots"] == 266
        assert int(player_shooting["xg"] * 10) == int(31.6 * 10)


class TestMatches:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Matches, typing.Any, None]:
        yield Matches(date="2023-09-03")

    def test_request(self, spider: Matches) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/matches/2023-09-03"

    def test_parse(self, spider: Matches) -> None:
        text = read_test_data("matches_2023-09-03.html")
        response = httpx.Response(200, text=text)
        matches = spider.parse(response)
        assert len(matches) == 18
        match = matches[0]
        assert match["id"] == "bdbc722e"
        assert match["name"] == "Liverpool vs Aston Villa"


class TestMatch:
    @pytest.fixture(scope="class")
    def spider(self) -> typing.Generator[Match, typing.Any, None]:
        yield Match(id="74125d47")

    def test_request(self, spider: Match) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/matches/74125d47"

    def test_parse(self, spider: Match) -> None:
        text = read_test_data("matches_74125d47.html")
        response = httpx.Response(200, text=text)
        match = spider.parse(response)
        assert match["id"] == "74125d47"
        assert match["name"] == "Arsenal vs Manchester United"
