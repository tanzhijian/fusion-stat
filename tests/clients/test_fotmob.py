import typing

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FotMob


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
