import json

import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.fusion import Competitions


@pytest.mark.asyncio
async def test_competitions_get(httpx_mock: HTTPXMock) -> None:
    with open("tests/data/fotmob/allLeagues.json") as f:
        data = json.load(f)
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/allLeagues", json=data
    )
    with open("tests/data/fbref/comps_.html") as f:
        data = f.read()
    httpx_mock.add_response(url="https://fbref.com/en/comps/", text=data)

    competitions = Competitions()
    coms = await competitions.get()
    assert len(coms.fotmob) == len(coms.fbref) == 6
    assert coms.fotmob[0].name == "Premier League"
    assert coms.fbref[0].id == "8"


@pytest.mark.asyncio
async def test_competitions_init_index(httpx_mock: HTTPXMock) -> None:
    with open("tests/data/fotmob/allLeagues.json") as f:
        data = json.load(f)
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/allLeagues", json=data
    )
    with open("tests/data/fbref/comps_.html") as f:
        data = f.read()
    httpx_mock.add_response(url="https://fbref.com/en/comps/", text=data)

    competitions = Competitions()
    index = await competitions._init_index()
    assert index["PL"]["fotmob"]["id"] == "47"
