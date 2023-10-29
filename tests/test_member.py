import typing

import httpx
import pytest_asyncio
from pytest_httpx import HTTPXMock

from .downloaders.test_fotmob import mock as fotmob_mock
from .downloaders.test_fbref import mock as fbref_mock
from fusion_stat.member import Response, Member
from fusion_stat.models import Params


@pytest_asyncio.fixture
async def response(
    client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("playerData?id=961995.json", httpx_mock)
    fbref_mock("players_bc7dc64d_Bukayo-Saka.html", httpx_mock)

    params = Params(
        fotmob_id="961995",
        fbref_id="bc7dc64d",
        fbref_path_name="Bukayo-Saka",
    )
    member = Member(params, client=client)
    response = await member.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Bukayo Saka"
