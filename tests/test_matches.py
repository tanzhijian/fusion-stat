import typing

import httpx
import pytest_asyncio
import respx

from .downloaders.test_fotmob import mock as fotmob_mock
from .downloaders.test_fbref import mock as fbref_mock
from fusion_stat.matches import Response, Matches


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("matches?date=20230903.json")
    fbref_mock("matches_2023-09-03.html")

    matches = Matches("2023-09-03", client=client)
    with respx.mock:
        response = await matches.get()
    yield response


def test_get(response: Response) -> None:
    assert len(response.fotmob) == len(response.fbref) + 1

    match_1 = response.fotmob[0]
    assert match_1.id == "4193495"
    assert match_1.name == "Crystal Palace vs Wolverhampton Wanderers"

    match_2 = response.fbref[0]
    assert match_2.id == "bdbc722e"
    assert match_2.name == "Liverpool vs Aston Villa"


def test_info(response: Response) -> None:
    info = response.info
    match = info["matches"][0]
    assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
    assert match["score"] == "3 - 2"


def test_index(response: Response) -> None:
    index = response.index()
    assert len(index) == 18
    params = index[0]
    assert params.fotmob_id == "4193495"
    assert params.fbref_id == "f9436d32"
