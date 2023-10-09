import asyncio
import typing
import json
from pathlib import Path

import pytest
import pytest_asyncio
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat import Competitions, Competition, Team, Member, Params
from fusion_stat.config import COMPETITIONS


def fotmob_mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fotmob/{file}")) as f:
        data = json.load(f)
    httpx_mock.add_response(
        url=f"https://www.fotmob.com/api/{file.split('.')[0]}",
        json=data,
    )


def fbref_mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    httpx_mock.add_response(
        url=f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}",
        text=text,
    )


@pytest.fixture(scope="class")
def event_loop() -> (
    typing.Generator[asyncio.AbstractEventLoop, typing.Any, None]
):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


class TestCompetitions:
    @pytest_asyncio.fixture(scope="class")
    async def competitions(
        self,
    ) -> typing.AsyncGenerator[Competitions, typing.Any]:
        async with httpx.AsyncClient() as client:
            yield Competitions(client)

    @pytest.mark.asyncio
    async def test_get(
        self, competitions: Competitions, httpx_mock: HTTPXMock
    ) -> None:
        fotmob_mock("allLeagues.json", httpx_mock)
        fbref_mock("comps_.html", httpx_mock)

        r = await competitions.get()
        assert len(r.fotmob) == len(COMPETITIONS)
        assert len(r.fbref) == len(COMPETITIONS)
        assert r.fotmob[0].name == "Premier League"

    def test_index(self, competitions: Competitions) -> None:
        index = competitions.index()
        assert index[0].fbref_path_name == "Premier-League"


class TestCompetition:
    @pytest.fixture(scope="class")
    def competition(self) -> typing.Generator[Competition, typing.Any, None]:
        params = Params(
            fotmob_id="47",
            fbref_id="9",
            fbref_path_name="Premier-League",
        )
        yield Competition(params)

    @pytest.mark.asyncio
    async def test_get(
        self, competition: Competition, httpx_mock: HTTPXMock
    ) -> None:
        fotmob_mock("leagues?id=47.json", httpx_mock)
        fbref_mock("comps_9_Premier-League-Stats.html", httpx_mock)

        r = await competition.get()
        assert r.fotmob.name == "Premier League"

    def test_info(self, competition: Competition) -> None:
        info = competition.info
        assert info["name"] == "Premier League"
        assert "Premier League" in info["names"]

    def test_teams(self, competition: Competition) -> None:
        teams = competition.teams
        assert len(teams) == 20
        assert teams["Manchester City"]["shooting"]["xg"] == 8.6

    def test_matches(self, competition: Competition) -> None:
        matches = competition.matches
        assert len(matches) == 380
        match = matches["Arsenal vs Manchester United"]
        assert match["score"] == "3 - 1"

    def test_teams_index(self, competition: Competition) -> None:
        index = competition.teams_index()
        assert len(index) == 20
        assert index[0].fotmob_id == "8456"

    def test_table(self, competition: Competition) -> None:
        table = competition.table
        city = table[0]
        assert city["name"] == "Manchester City"
        assert city["draws"] == 0
        assert city["goals_for"] == 11
        assert city["xg"] == 8.6

        chelsea = table[11]
        assert chelsea["name"] == "Chelsea"
        assert chelsea["played"] == 4
        assert chelsea["losses"] == 2
        assert chelsea["goals_against"] == 5
        assert chelsea["points"] == 4
        assert chelsea["xg"] == 8.3


class TestTeam:
    @pytest.fixture(scope="class")
    def team(self) -> typing.Generator[Team, typing.Any, None]:
        params = Params(
            fotmob_id="9825",
            fbref_id="18bb7c10",
            fbref_path_name="Arsenal",
        )
        yield Team(params)

    @pytest.mark.asyncio
    async def test_get(self, team: Team, httpx_mock: HTTPXMock) -> None:
        fotmob_mock("teams?id=9825.json", httpx_mock)
        fbref_mock("squads_18bb7c10_Arsenal-Stats.html", httpx_mock)

        r = await team.get()
        assert r.fotmob.name == "Arsenal"
        assert r.fbref.shooting.xg == 8.3

        assert len(r.fotmob.members) == 26
        coach = r.fotmob.members[0]
        assert coach.is_staff
        player = r.fotmob.members[1]
        assert not player.is_staff

        saka = r.fbref.members[4]
        assert int(saka.shooting.shots) == 11

    def test_staff(self, team: Team) -> None:
        staff = team.staff
        assert staff[0]["name"] == "Mikel Arteta"
        assert staff[0]["country"] == "Spain"

    def test_players(self, team: Team) -> None:
        players = team.players
        assert len(players) == 21


class TestMember:
    @pytest.fixture(scope="class")
    def member(self) -> typing.Generator[Member, typing.Any, None]:
        params = Params(
            fotmob_id="961995",
            fbref_id="bc7dc64d",
            fbref_path_name="Bukayo-Saka",
        )
        yield Member(params)

    @pytest.mark.asyncio
    async def test_get(self, member: Member, httpx_mock: HTTPXMock) -> None:
        fotmob_mock("playerData?id=961995.json", httpx_mock)
        fbref_mock("players_bc7dc64d_Bukayo-Saka.html", httpx_mock)

        r = await member.get()
        assert r.fotmob.name == "Bukayo Saka"
