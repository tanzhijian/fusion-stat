import typing

import pytest
import pytest_asyncio
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders import FBref
from fusion_stat.models import Params

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

    params = Params(
        fotmob_id="47",
        fbref_id="9",
        fbref_path_name="Premier-League",
    )
    r = await fbref.get_competition(params)
    assert r.status_code == 200

    r = await fbref.get_competition(params, "2022-2023")
    assert r.status_code == 200

    params = Params(fotmob_id="47", fbref_id="9")
    r = await fbref.get_competition(params)
    assert r.status_code == 200

    r = await fbref.get_competition(params, "2022-2023")
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

    params = Params(
        fotmob_id="47",
        fbref_id="18bb7c10",
        fbref_path_name="Arsenal",
    )
    r = await fbref.get_team(params)
    assert r.status_code == 200

    r = await fbref.get_team(params, season="2022-2023")
    assert r.status_code == 200

    params = Params(fotmob_id="47", fbref_id="18bb7c10")
    r = await fbref.get_team(params)
    assert r.status_code == 200

    r = await fbref.get_team(params, season="2022-2023")
    assert r.status_code == 200
