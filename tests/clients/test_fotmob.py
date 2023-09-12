import json
import typing
from pathlib import Path

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FotMob


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="session")
async def fotmob() -> typing.AsyncGenerator[FotMob, typing.Any]:
    async with FotMob() as fm:
        yield fm


def mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fotmob/{file}")) as f:
        data = json.load(f)
    httpx_mock.add_response(
        url=f"https://www.fotmob.com/api/{file.split('.')[0]}",
        json=data,
    )


async def test_get_competition(fotmob: FotMob, httpx_mock: HTTPXMock) -> None:
    mock("leagues?id=47.json", httpx_mock)
    competition = await fotmob.get_competition("47")
    assert competition.name == "Premier League"


async def test_get_team(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    mock("teams?id=9825.json", httpx_mock)
    team = await fotmob.get_team("9825")
    assert team.name == "Arsenal"


async def test_get_player(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    mock("playerData?id=961995.json", httpx_mock)
    player = await fotmob.get_player("961995")
    assert player.name == "Bukayo Saka"


async def test_get_matches(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    mock("matches?date=20230903.json", httpx_mock)
    matches = await fotmob.get_matches("20230903")
    assert matches.date == "20230903"


async def test_get_match(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    mock("matchDetails?matchId=4193490.json", httpx_mock)
    match = await fotmob.get_match("4193490")
    assert match.home_team == "Arsenal"
