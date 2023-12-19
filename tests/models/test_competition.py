import httpx
import pytest

from fusion_stat import Competition
from fusion_stat.spiders import fbref, fotmob, official
from tests.utils import read_data


def test_sort_table_key() -> None:
    key = Competition.sort_table_key(
        {
            "name": "A",
            "points": 20,
            "goals_for": 20,
            "goals_against": 10,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "xg": 0,
        }
    )
    assert key[0] == -20


class TestCompetition:
    @pytest.fixture(scope="class")
    def competition(self, client: httpx.AsyncClient) -> Competition:
        fotmob_data = read_data("fotmob", "leagues?id=47.json")
        fbref_data = read_data("fbref", "comps_9_Premier-League-Stats.html")
        official_data = read_data(
            "premier_league",
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json",
        )
        fotmob_spider = fotmob.Competition(id="47", client=client)
        fbref_spider = fbref.Competition(
            id="9", path_name="Premier-League", client=client
        )
        official_spider = official.Competition(
            name="Premier League", client=client
        )
        return Competition(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            official=official_spider.parse(
                httpx.Response(200, json=official_data)
            ),
        )

    def test_info(self, competition: Competition) -> None:
        info = competition.info
        assert info["name"] == "Premier League"
        assert "Premier League" in info["names"]
        assert info["logo"]

    def test_teams(self, competition: Competition) -> None:
        teams = competition.teams
        assert len(teams) == 20
        team = teams[0]
        assert team["name"] == "Manchester City"
        assert int(team["shooting"]["xg"]) == int(8.6)
        assert (
            team["logo"]
            == "https://resources.premierleague.com/premierleague/badges/rb/t43.svg"
        )

    def test_matches(self, competition: Competition) -> None:
        matches = competition.matches
        assert len(matches) == 380
        match = matches[0]
        assert match["score"] == "0 - 3"

    def test_teams_index(self, competition: Competition) -> None:
        index = competition.teams_index()
        assert len(index) == 20
        assert index[0]["fotmob_id"] == "8456"

    def test_table(self, competition: Competition) -> None:
        table = competition.table
        city = table[0]
        assert city["name"] == "Manchester City"
        assert city["draws"] == 0
        assert city["goals_for"] == 11
        assert int(city["xg"]) == int(8.6)

        chelsea = table[11]
        assert chelsea["name"] == "Chelsea"
        assert chelsea["played"] == 4
        assert chelsea["losses"] == 2

        assert chelsea["goals_against"] == 5
        assert chelsea["points"] == 4
        assert int(chelsea["xg"]) == int(8.3)
