import httpx
import pytest

from fusion_stat import Team
from fusion_stat.spiders import fbref, fotmob, transfermarkt
from fusion_stat.types import team_types
from tests.utils import read_data


class TestTeam:
    @pytest.fixture(scope="class")
    def team(self) -> Team:
        fotmob_data = read_data("fotmob", "teams?id=9825.json")
        fbref_data = read_data("fbref", "squads_18bb7c10_Arsenal-Stats.html")
        transfermarkt_data = read_data(
            "transfermarkt", "arsenal-fc_startseite_verein_11.html"
        )
        transfermarkt_staffs_data = read_data(
            "transfermarkt", "ceapi_staff_team_11_.json"
        )

        fotmob_spider = fotmob.Team(id="9825")
        fbref_spider = fbref.Team(id="18bb7c10", path_name="Arsenal")
        transfermarkt_spider = transfermarkt.Team(
            id="11", path_name="arsenal-fc"
        )
        transfermarkt_staffs_spider = transfermarkt.Staffs(id="11")

        return Team(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
            transfermarkt_staffs=transfermarkt_staffs_spider.parse(
                httpx.Response(200, json=transfermarkt_staffs_data)
            ),
        )

    def test_find_player(self, team: Team) -> None:
        query = team_types.BasePlayerDict(
            id="1", name="ab", country_code="a", position="ab"
        )
        choices = [
            team_types.BasePlayerDict(
                id="2", name="abc", country_code="a", position="abc"
            ),
            team_types.BasePlayerDict(
                id="3", name="c", country_code="c", position="c"
            ),
        ]
        result = team._find_player(query, choices)
        assert result["id"] == "2"

    def test_info(self, team: Team) -> None:
        info = team.info
        assert info["id"] == "9825"
        assert info["name"] == "Arsenal"
        assert "Arsenal" in info["names"]
        assert info["country_code"] == "ENG"
        assert info["market_values"] == "€1.12bn"

    def test_get_staffs(self, team: Team) -> None:
        staff = next(team.get_staffs())
        assert staff["id"] == "47620"
        assert staff["name"] == "Mikel Arteta"
        assert staff["position"] == "Manager"

    def test_staffs(self, team: Team) -> None:
        assert len(team.staffs) == 54

    def test_get_players(self, team: Team) -> None:
        players = team.get_players()
        player = next(players)
        assert player["name"] == "David Raya"

    def test_players(self, team: Team) -> None:
        players = team.players
        assert len(players) == 23
        player = players[-1]
        assert player["id"] == "1021586"
        assert player["name"] == "Gabriel Martinelli"
        assert "Gabriel Martinelli" in player["names"]
        assert player["country"] == "Brazil"
        assert player["position"] == "FW"
        assert player["date_of_birth"] == "2001-06-18"
        assert player["market_values"] == "€85.00m"

    def test_get_players_params(self, team: Team) -> None:
        params = team.get_players_params()
        player = next(params)
        assert player["fotmob_id"] == "562727"
        assert player["fbref_id"] == "98ea5115"
        assert player["fbref_path_name"] == "David-Raya"
        assert player["transfermarkt_id"] == "262749"
        assert player["transfermarkt_path_name"] == "david-raya"

    def test_get_staffs_params(self, team: Team) -> None:
        params = team.get_staffs_params()
        staff = next(params)
        assert staff["transfermarkt_id"] == "47620"
        assert staff["transfermarkt_path_name"] == "mikel-arteta"
