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


async def test_get_competition(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("comps_9_Premier-League-Stats.html", httpx_mock)
    competition = await fbref.get_competition("9", "Premier-League")
    assert len(competition) > 0

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
    mock("squads_18bb7c10_Arsenal-Stats.html", httpx_mock)
    team = await fbref.get_team("18bb7c10", "Arsenal")
    assert len(team) > 0

    httpx_mock.add_response(
        url="https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats",
        text="arsenal 2022",
    )
    team = await fbref.get_team("18bb7c10", "Arsenal", "2022-2023")
    assert team == "arsenal 2022"


async def test_get_player(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("players_bc7dc64d_Bukayo-Saka.html", httpx_mock)
    player = await fbref.get_player("bc7dc64d", "Bukayo-Saka")
    assert len(player) > 0


async def test_get_matches(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("matches_2023-09-03.html", httpx_mock)
    matches = await fbref.get_matches("2023-09-03")
    assert len(matches) > 0


async def test_get_match(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    mock("matches_74125d47.html", httpx_mock)
    match = await fbref.get_match("74125d47")
    assert len(match) > 0
