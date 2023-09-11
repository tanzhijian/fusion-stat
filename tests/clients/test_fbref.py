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
        url="https://fbref.com/en/comps/9/Premier-League-Stats", text="pl"
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
