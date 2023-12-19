import httpx
import pytest

from fusion_stat import Team
from fusion_stat.spiders.fbref import Team as FBrefTeam
from fusion_stat.spiders.fotmob import Team as FotMobTeam
from tests.utils import read_data


class TestTeam:
    @pytest.fixture(scope="class")
    def team(self, client: httpx.AsyncClient) -> Team:
        fotmob_data = read_data("fotmob", "teams?id=9825.json")
        fbref_data = read_data("fbref", "squads_18bb7c10_Arsenal-Stats.html")

        fotmob = FotMobTeam(id="9825", client=client)
        fbref = FBrefTeam(id="18bb7c10", path_name="Arsenal", client=client)

        return Team(
            fotmob=fotmob.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref.parse(httpx.Response(200, text=fbref_data)),
        )

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

    def test_members_index(self, team: Team) -> None:
        index = team.members_index()
        params = index[0]
        assert params["fotmob_id"] == "562727"
        assert params["fbref_id"] == "98ea5115"
        assert params["fbref_path_name"] == "David-Raya"
