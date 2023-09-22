import typing

import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.fusion import Competitions, Competition
from tests.clients.test_fotmob import mock as fotmob_mock
from tests.clients.test_fbref import mock as fbref_mock


class TestCompetitions:
    @pytest.fixture(scope="class")
    def competitions(self) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions()

    @pytest.mark.asyncio
    async def test_get(
        self, competitions: Competitions, httpx_mock: HTTPXMock
    ) -> None:
        fotmob_mock("allLeagues.json", httpx_mock)
        fbref_mock("comps_.html", httpx_mock)

        coms = await competitions.get()
        assert len(coms.fotmob) == len(coms.fbref) == 6
        assert coms.fotmob[0].name == "Premier League"
        assert coms.fbref[0].id == "8"

    def test_parse_index(self, competitions: Competitions) -> None:
        if not competitions.data:
            raise ValueError
        index = competitions._parse_index(competitions.data)
        assert index["PL"]["fotmob"]["id"] == "47"


class TestCompetition:
    @pytest.fixture(scope="class")
    def competition(self) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition("PL")

    @pytest.mark.asyncio
    async def test_get(
        self, competition: Competition, httpx_mock: HTTPXMock
    ) -> None:
        fotmob_mock("leagues?id=47.json", httpx_mock)
        fbref_mock("comps_9_Premier-League-Stats.html", httpx_mock)

        com = await competition.get()
        assert com.id == "PL"
