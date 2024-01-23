import httpx
import pytest

from fusion_stat import Competition
from fusion_stat.spiders import fbref, fotmob, official, transfermarkt
from fusion_stat.types import base_types
from tests.utils import read_data


def test_sort_table_key() -> None:
    key = Competition.sort_table_key(
        {
            "id": "4",
            "name": "A",
            "points": 20,
            "goals_for": 20,
            "goals_against": 10,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "logo": "https://a.png",
            "xg": 0,
        }
    )
    assert key[0] == -20


class TestCompetition:
    @pytest.fixture(scope="class")
    def competition(self) -> Competition:
        fotmob_data = read_data("fotmob", "leagues?id=47.json")
        fbref_data = read_data("fbref", "comps_9_Premier-League-Stats.html")
        official_data = read_data(
            "premier_league",
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json",
        )
        transfermarkt_data = read_data(
            "transfermarkt", "premier-league_startseite_wettbewerb_GB1.html"
        )
        fotmob_spider = fotmob.Competition(id="47")
        fbref_spider = fbref.Competition(id="9", path_name="Premier-League")
        official_spider = official.Competition(name="Premier League")
        transfermarkt_spider = transfermarkt.Competition(
            id="GB1", path_name="premier-league"
        )
        return Competition(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            official=official_spider.parse(
                httpx.Response(200, json=official_data)
            ),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
        )

    def test_find_team(self, competition: Competition) -> None:
        query: base_types.StatDict = {"id": "1", "name": "ab"}
        choices: list[base_types.StatDict] = [
            {"id": "2", "name": "abc"},
            {"id": "3", "name": "c"},
        ]
        result = competition._find_team(query, choices)
        assert result["id"] == "2"

    def test_info(self, competition: Competition) -> None:
        info = competition.info
        assert info["id"] == "47"
        assert info["name"] == "Premier League"
        assert info["country_code"] == "ENG"
        assert "Premier League" in info["names"]
        assert info["logo"]
        assert info["market_values"] == "€10.99bn"
        assert info["player_average_market_value"] == "€19.27m"

    def test_get_teams(self, competition: Competition) -> None:
        teams = competition.get_teams()
        team = next(teams)
        assert team["id"] == "8456"
        assert team["name"] == "Manchester City"
        assert team["country_code"] == "ENG"
        assert team["market_values"] == "€1.29bn"
        assert int(team["shooting"]["xg"]) == int(8.6)
        assert (
            team["logo"]
            == "https://resources.premierleague.com/premierleague/badges/rb/t43.svg"
        )

    def test_teams(self, competition: Competition) -> None:
        assert len(competition.teams) == 20

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

    def test_get_matches(self, competition: Competition) -> None:
        matches = competition.get_matches()
        match = next(matches)
        assert match["id"] == "4193450"
        assert match["competition"]["id"] == "47"
        assert match["home"]["id"] == "8191"
        assert match["home"]["score"] == 0
        assert match["away"]["id"] == "8456"
        assert match["away"]["score"] == 3

    def test_matches(self, competition: Competition) -> None:
        assert len(competition.matches) == 380

    def test_get_teams_params(self, competition: Competition) -> None:
        params = competition.get_teams_params()
        team = next(params)
        assert team["fotmob_id"] == "8456"
        assert team["fbref_id"] == "b8fd03ef"
        assert team["fbref_path_name"] == "Manchester-City"
        assert team["transfermarkt_id"] == "281"
        assert team["transfermarkt_path_name"] == "manchester-city"
