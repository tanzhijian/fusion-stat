import typing

import pytest_asyncio
import respx

from fusion_stat import Fusion, Team
from tests.utils import fbref_mock, fotmob_mock


class TestTeam:
    @pytest_asyncio.fixture(scope="class")
    async def team(
        self, fusion: Fusion
    ) -> typing.AsyncGenerator[Team, typing.Any]:
        fotmob_mock("teams?id=9825.json")
        fbref_mock("squads_18bb7c10_Arsenal-Stats.html")

        params = {
            "fotmob_id": "9825",
            "fbref_id": "18bb7c10",
            "fbref_path_name": "Arsenal",
        }
        with respx.mock:
            team = await fusion.get_team(**params)
        yield team

    def test_get(self, team: Team) -> None:
        assert team.fotmob.name == "Arsenal"
        assert int(team.fbref.shooting.xg) == int(8.3)

        assert len(team.fotmob.members) == 26
        coach = team.fotmob.members[0]
        assert coach.is_staff
        player = team.fotmob.members[1]
        assert not player.is_staff
        assert player.position == "GK"
        assert player.country == "Spain"

        saka = team.fbref.members[4]
        assert saka.position == "FW"
        assert saka.country_code == "ENG"
        assert saka.path_name == "Bukayo-Saka"
        assert int(saka.shooting.shots) == 11

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
