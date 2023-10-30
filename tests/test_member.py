import typing

import httpx
import pytest_asyncio
import respx

from .spiders.test_fotmob import mock as fotmob_mock
from .spiders.test_fbref import mock as fbref_mock
from fusion_stat.member import Response, Member
from fusion_stat.models import Params


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("playerData?id=961995.json")
    fbref_mock("players_bc7dc64d_Bukayo-Saka.html")

    params = Params(
        fotmob_id="961995",
        fbref_id="bc7dc64d",
        fbref_path_name="Bukayo-Saka",
    )
    member = Member(params, client=client)
    with respx.mock:
        response = await member.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Bukayo Saka"
