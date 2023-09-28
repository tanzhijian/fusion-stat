import typing
import json
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.fusion import Competitions, Competition
from fusion_stat.config import COMPETITIONS
from fusion_stat.models import Params


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
        assert competition.teams["Manchester City"]["shooting"]["xg"] == 8.6

    def test_matches(self, competition: Competition) -> None:
        assert len(competition.matches) == 380
        match = competition.matches["Arsenal vs Manchester United"]
        assert match["score"] == "3 - 1"
