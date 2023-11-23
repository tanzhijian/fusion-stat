import typing

import httpx
import pytest_asyncio
import respx

from fusion_stat.match import Fusion, Match

from .utils import fbref_mock, fotmob_mock


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("matchDetails?matchId=4193490.json")
    fbref_mock("matches_74125d47.html")

    match = Match(fotmob_id="4193490", fbref_id="74125d47", client=client)
    with respx.mock:
        fusion = await match.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert fusion.fotmob.name == "Arsenal vs Manchester United"
    assert fusion.fbref.name == "Arsenal vs Manchester United"
