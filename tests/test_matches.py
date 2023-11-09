import typing

import httpx
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.matches import Fusion, Matches


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("matches?date=20230903.json")
    fbref_mock("matches_2023-09-03.html")

    matches = Matches(date="2023-09-03", client=client)
    with respx.mock:
        fusion = await matches.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert len(fusion.fotmob) == len(fusion.fbref) + 1

    match_1 = fusion.fotmob[0]
    assert match_1.id == "4193495"
    assert match_1.name == "Crystal Palace vs Wolverhampton Wanderers"

    match_2 = fusion.fbref[0]
    assert match_2.id == "bdbc722e"
    assert match_2.name == "Liverpool vs Aston Villa"


def test_info(fusion: Fusion) -> None:
    info = fusion.info
    match = info["matches"][0]
    assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
    assert match["score"] == "3 - 2"


def test_index(fusion: Fusion) -> None:
    index = fusion.index()
    assert len(index) == 18
    params = index[0]
    assert params["fotmob_id"] == "4193495"
    assert params["fbref_id"] == "f9436d32"
