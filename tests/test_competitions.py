import typing

import pytest_asyncio
from pytest_httpx import HTTPXMock

from .downloaders.test_fotmob import mock as fotmob_mock
from .downloaders.test_fbref import mock as fbref_mock
from fusion_stat.competitions import Response, Competitions


# pytest_httpx 不能使用更高级别的 scope
@pytest_asyncio.fixture
async def response(
    httpx_mock: HTTPXMock,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("allLeagues.json", httpx_mock)
    fbref_mock("comps_.html", httpx_mock)

    coms = Competitions()
    response = await coms.get()
    yield response


def test_get(response: Response) -> None:
    assert len(response.fotmob) > 0


def test_index(response: Response) -> None:
    index = response.index()
    assert index[0].fbref_path_name == "Premier-League"
