import typing

import httpx
import pytest_asyncio
import respx

from fusion_stat import Competition, Fusion
from tests.utils import fbref_mock, fotmob_mock, premier_league_mock


class TestCompetition:
    @pytest_asyncio.fixture(scope="class")
    async def competition(
        self,
        client: httpx.AsyncClient,
    ) -> typing.AsyncGenerator[Competition, typing.Any]:
        fotmob_mock("leagues?id=47.json")
        fbref_mock("comps_9_Premier-League-Stats.html")
        premier_league_mock(
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json"
        )
        fusion = Fusion(client=client)

        with respx.mock:
            com = await fusion.get_competition(
                fotmob_id="47",
                fbref_id="9",
                fbref_path_name="Premier-League",
                official_name="Premier League",
            )
        yield com

    def test_get(self, competition: Competition) -> None:
        assert competition.fotmob.name == "Premier League"

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
