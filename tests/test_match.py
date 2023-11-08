import typing

import httpx
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.match import Response, Match


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("matchDetails?matchId=4193490.json")
    fbref_mock("matches_74125d47.html")

    match = Match(fotmob_id="4193490", fbref_id="74125d47", client=client)
    with respx.mock:
        response = await match.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Arsenal vs Manchester United"
    assert response.fbref.name == "Arsenal vs Manchester United"
