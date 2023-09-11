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


async def test_get_competition(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/comps/9/Premier-League-Stats",
        text="pl",
    )
    competition = await fbref.get_competition("9", "Premier-League")
    assert competition == "pl"

    httpx_mock.add_response(
        url=(
            "https://fbref.com/en/comps/9/2022-2023/"
            "2022-2023-Premier-League-Stats"
        ),
        text="pl 2022",
    )
    competition = await fbref.get_competition(
        "9", "Premier-League", "2022-2023"
    )
    assert competition == "pl 2022"


async def test_get_team(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/squads/18bb7c10/Arsenal-Stats",
        text="arsenal",
    )
    team = await fbref.get_team("18bb7c10", "Arsenal")
    assert team == "arsenal"

    httpx_mock.add_response(
        url="https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats",
        text="arsenal 2022",
    )
    team = await fbref.get_team("18bb7c10", "Arsenal", "2022-2023")
    assert team == "arsenal 2022"


async def test_get_player(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/players/bc7dc64d/Bukayo-Saka",
        text="saka",
    )
    player = await fbref.get_player("bc7dc64d", "Bukayo-Saka")
    assert player == "saka"


async def test_get_matches(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/2023-09-03",
        text="20230903",
    )
    matches = await fbref.get_matches("2023-09-03")
    assert matches == "20230903"


async def test_get_match(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/74125d47",
        text="Arsenal vs Man United",
    )
    matches = await fbref.get_matches("74125d47")
    assert matches == "Arsenal vs Man United"
