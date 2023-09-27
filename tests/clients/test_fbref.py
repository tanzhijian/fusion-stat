import typing

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FBref


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def fbref() -> typing.AsyncGenerator[FBref, typing.Any]:
    async with FBref() as fb:
        yield fb


async def test_get_competitions(httpx_mock: HTTPXMock, fbref: FBref) -> None:
    httpx_mock.add_response(url="https://fbref.com/en/comps/", text="halo")
    r = await fbref.get_competitions()
    assert r.status_code == 200
