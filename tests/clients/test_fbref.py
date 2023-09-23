import typing

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FBref


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="session")
async def fbref() -> typing.AsyncGenerator[FBref, typing.Any]:
    async with FBref() as fb:
        yield fb


async def test_get_competitions(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(url="https://fbref.com/en/comps/", text="halo")
    r = await fbref.get_competitions()
    assert r.status_code == 200


async def test_get_competition(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/comps/9/Premier-League-Stats", text="halo"
    )
    r = await fbref.get_competition("PL")
    assert r.status_code == 200


async def test_get_team(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/squads/18bb7c10/Arsenal-Stats", text="halo"
    )
    r = await fbref.get_team("18bb7c10", "Arsenal")
    assert r.status_code == 200


async def test_get_player(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/players/bc7dc64d/Bukayo-Saka", text="halo"
    )
    r = await fbref.get_player("bc7dc64d", "Bukayo-Saka")
    assert r.status_code == 200


async def test_get_matches(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/2023-09-03", text="halo"
    )
    r = await fbref.get_matches("2023-09-03")
    assert r.status_code == 200


async def test_get_match(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/74125d47", text="halo"
    )
    r = await fbref.get_match("74125d47")
    assert r.status_code == 200
