import httpx
import pytest

from fusion_stat import Team
from fusion_stat.spiders import fbref, fotmob, transfermarkt
from tests.utils import read_data


class TestTeam:
    @pytest.fixture(scope="class")
    def team(self, client: httpx.AsyncClient) -> Team:
        fotmob_data = read_data("fotmob", "teams?id=9825.json")
        fbref_data = read_data("fbref", "squads_18bb7c10_Arsenal-Stats.html")
        transfermarkt_data = read_data(
            "transfermarkt", "arsenal-fc_startseite_verein_11.html"
        )

        fotmob_spider = fotmob.Team(id="9825", client=client)
        fbref_spider = fbref.Team(
            id="18bb7c10", path_name="Arsenal", client=client
        )
        transfermarkt_spider = transfermarkt.Team(
            id="11", path_name="arsenal-fc", client=client
        )

        return Team(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
        )

    def test_info(self, team: Team) -> None:
        info = team.info
        assert info["id"] == "ENG_Arsenal"
        assert info["name"] == "Arsenal"
        assert "Arsenal" in info["names"]
        assert info["country_code"] == "ENG"

    def test_staff(self, team: Team) -> None:
        staff = team.staff
        assert staff[0]["name"] == "Mikel Arteta"
        assert staff[0]["country"] == "Spain"

    def test_players(self, team: Team) -> None:
        players = team.players
        assert len(players) == 23
        martin = players[-1]
        assert martin["name"] == "Gabriel Martinelli"
        assert "Gabriel Martinelli" in martin["names"]

    def test_get_members_params(self, team: Team) -> None:
        params = team.get_members_params()
        member = params[0]
        assert member["fotmob_id"] == "562727"
        assert member["fbref_id"] == "98ea5115"
        assert member["fbref_path_name"] == "David-Raya"
