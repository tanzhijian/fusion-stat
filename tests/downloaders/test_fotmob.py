import typing

import pytest
import pytest_asyncio
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders import FotMob
from fusion_stat.models import Params


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def fotmob() -> typing.AsyncGenerator[FotMob, typing.Any]:
    async with FotMob(httpx.AsyncClient()) as fm:
        yield fm


async def test_get_competitions(fotmob: FotMob, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/allLeagues", json={"foo": "bar"}
    )
    r = await fotmob.get_competitions()
    assert r.status_code == 200


async def test_get_competition(fotmob: FotMob, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/leagues?id=47", json={"foo": "bar"}
    )

    params = Params(fotmob_id="47", fbref_id="9", fbref_path_name="pl")
    r = await fotmob.get_competition(params)
    assert r.status_code == 200


async def test_get_team(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/teams?id=9825", json={"foo": "bar"}
    )

    params = {"fotmob_id": "9825", "fbref_id": "9", "fbref_path_name": "pl"}
    r = await fotmob.get_team(params)
    assert r.status_code == 200


async def test_get_player(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/playerData?id=961995",
        json={"foo": "bar"},
    )

    params = {"fotmob_id": "961995", "fbref_id": "9", "fbref_path_name": "pl"}
    r = await fotmob.get_member(params)
    assert r.status_code == 200


async def test_get_matches(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/matches?date=20230903",
        json={"foo": "bar"},
    )

    r = await fotmob.get_matches("2023-09-03")
    assert r.status_code == 200


async def test_get_match(httpx_mock: HTTPXMock, fotmob: FotMob) -> None:
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/matchDetails?matchId=4193490",
        json={"foo": "bar"},
    )

    params = {"fotmob_id": "4193490", "fbref_id": "9"}
    r = await fotmob.get_match(params)
    assert r.status_code == 200
