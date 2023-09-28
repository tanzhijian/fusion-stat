import typing

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FotMob
from fusion_stat.models import Params, Feature, FBrefFeature


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def fotmob() -> typing.AsyncGenerator[FotMob, typing.Any]:
    async with FotMob() as fm:
        yield fm


async def test_get_competitions(fotmob: FotMob, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/allLeagues", json={"foo": "bar"}
    )
    r = await fotmob.get_competitions()
    assert r.status_code == 200


async def test_get_competition(fotmob: FotMob, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/leagues?id=47", json={"foo": "bar"}
    )

    params = Params(
        fotmob=Feature(id="47"), fbref=FBrefFeature(id="9", path_name="pl")
    )
    r = await fotmob.get_competition(params)
    assert r.status_code == 200
