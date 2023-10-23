import typing

import pytest
import pytest_asyncio
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders import FBref

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def fbref() -> typing.AsyncGenerator[FBref, typing.Any]:
    async with FBref(httpx.AsyncClient()) as fb:
        yield fb


async def test_get_competitions(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(url="https://fbref.com/en/comps/", text="halo")
    r = await fbref.get_competitions()
    assert r.status_code == 200


async def test_get_competition(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    urls = (
        "https://fbref.com/en/comps/9/2022-2023",
        "https://fbref.com/en/comps/9",
        "https://fbref.com/en/comps/9/Premier-League-Stats",
        (
            "https://fbref.com/en/comps/9/2022-2023/"
            "2022-2023-Premier-League-Stats"
        ),
    )
    for url in urls:
        httpx_mock.add_response(url=url, text="halo")

    r = await fbref.get_competition("9", path_name="Premier-League")
    assert r.status_code == 200

    r = await fbref.get_competition(
        "9", season="2022-2023", path_name="Premier-League"
    )
    assert r.status_code == 200

    r = await fbref.get_competition("9")
    assert r.status_code == 200

    r = await fbref.get_competition("9", season="2022-2023")
    assert r.status_code == 200


async def test_get_team(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    urls = (
        "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats",
        "https://fbref.com/en/squads/18bb7c10",
        "https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats",
        "https://fbref.com/en/squads/18bb7c10/2022-2023",
    )
    for url in urls:
        httpx_mock.add_response(url=url, text="halo")

    r = await fbref.get_team("18bb7c10", path_name="Arsenal")
    assert r.status_code == 200

    r = await fbref.get_team(
        "18bb7c10", path_name="Arsenal", season="2022-2023"
    )
    assert r.status_code == 200

    r = await fbref.get_team("18bb7c10")
    assert r.status_code == 200

    r = await fbref.get_team("18bb7c10", season="2022-2023")
    assert r.status_code == 200


async def test_player(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    urls = (
        "https://fbref.com/en/players/bc7dc64d/",
        "https://fbref.com/en/players/bc7dc64d/Bukayo-Saka",
    )
    for url in urls:
        httpx_mock.add_response(url=url, text="halo")

    r = await fbref.get_member("bc7dc64d")
    assert r.status_code == 200

    r = await fbref.get_member("bc7dc64d", path_name="Bukayo-Saka")
    assert r.status_code == 200


async def test_matches(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/2023-09-03",
        text="halo",
    )

    r = await fbref.get_matches("2023-09-03")
    assert r.status_code == 200


async def test_match(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(
        url="https://fbref.com/en/matches/74125d47",
        text="halo",
    )

    r = await fbref.get_match("74125d47")
    assert r.status_code == 200
