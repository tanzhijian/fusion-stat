import typing

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FBref
from fusion_stat.models import Params, Feature, FBrefFeature

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
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
    httpx_mock.add_response(
        url=(
            "https://fbref.com/en/comps/9/2022-2023/"
            "2022-2023-Premier-League-Stats"
        ),
        text="halo",
    )

    params = Params(
        fotmob=Feature(id="47"),
        fbref=FBrefFeature(id="9", path_name="Premier-League"),
    )
    r = await fbref.get_competition(params)
    assert r.status_code == 200

    r = await fbref.get_competition(params, "2022-2023")
