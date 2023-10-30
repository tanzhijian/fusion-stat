import typing

import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.competitions import Response, Competitions


@pytest_asyncio.fixture(scope="module")
async def response() -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("allLeagues.json")
    fbref_mock("comps_.html")

    coms = Competitions()
    with respx.mock:
        response = await coms.get()
    yield response


def test_get(response: Response) -> None:
    assert len(response.fotmob) > 0


def test_index(response: Response) -> None:
    index = response.index()
    assert index[0].fbref_path_name == "Premier-League"
