import typing

import httpx
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.member import Response, Member


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("playerData?id=961995.json")
    fbref_mock("players_bc7dc64d_Bukayo-Saka.html")

    member = Member(
        fotmob_id="961995",
        fbref_id="bc7dc64d",
        fbref_path_name="Bukayo-Saka",
        client=client,
    )
    with respx.mock:
        response = await member.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Bukayo Saka"
