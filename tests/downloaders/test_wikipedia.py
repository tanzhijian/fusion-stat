import typing

import pytest
import pytest_asyncio
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders import Wikipedia

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def wikipedia() -> typing.AsyncGenerator[Wikipedia, typing.Any]:
    async with Wikipedia(httpx.AsyncClient()) as wiki:
        yield wiki


async def test_get_competition(
    wikipedia: Wikipedia, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://en.wikipedia.org/wiki/2023-24_Premier_League", text="halo"
    )

    r = await wikipedia.get_competition("Premier_League")
    assert r.status_code == 200
