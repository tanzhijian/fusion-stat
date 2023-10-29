import typing

import httpx
import pytest_asyncio
from pytest_httpx import HTTPXMock

from .downloaders.test_fotmob import mock as fotmob_mock
from .downloaders.test_fbref import mock as fbref_mock
from fusion_stat.match import Response, Match
from fusion_stat.models import Params


@pytest_asyncio.fixture
async def response(
    client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("matchDetails?matchId=4193490.json", httpx_mock)
    fbref_mock("matches_74125d47.html", httpx_mock)

    params = Params(
        fotmob_id="4193490",
        fbref_id="74125d47",
    )
    match = Match(params, client=client)
    response = await match.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Arsenal vs Manchester United"
    assert response.fbref.name == "Arsenal vs Manchester United"
