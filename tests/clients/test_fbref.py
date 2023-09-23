import typing
from pathlib import Path

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FBref


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="session")
async def fbref() -> typing.AsyncGenerator[FBref, typing.Any]:
    async with FBref() as fb:
        yield fb


def mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    httpx_mock.add_response(
        url=f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}",
        text=text,
    )


async def test_get_competitions(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("comps_.html", httpx_mock)
    r = await fbref.get_competitions()
    assert r.status_code == 200


async def test_get_competition(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("comps_9_Premier-League-Stats.html", httpx_mock)
    r = await fbref.get_competition("PL")
    assert r.status_code == 200


async def test_get_team(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("squads_18bb7c10_Arsenal-Stats.html", httpx_mock)
    r = await fbref.get_team("18bb7c10", "Arsenal")
    assert r.status_code == 200


async def test_get_player(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("players_bc7dc64d_Bukayo-Saka.html", httpx_mock)
    r = await fbref.get_player("bc7dc64d", "Bukayo-Saka")
    assert r.status_code == 200


async def test_get_matches(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("matches_2023-09-03.html", httpx_mock)
    r = await fbref.get_matches("2023-09-03")
    assert r.status_code == 200


async def test_get_match(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("matches_74125d47.html", httpx_mock)
    r = await fbref.get_match("74125d47")
    assert r.status_code == 200
