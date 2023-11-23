import typing

import httpx
import pytest_asyncio
import respx

from fusion_stat.member import Fusion, Member

from .utils import fbref_mock, fotmob_mock


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("playerData?id=961995.json")
    fbref_mock("players_bc7dc64d_Bukayo-Saka.html")

    member = Member(
        fotmob_id="961995",
        fbref_id="bc7dc64d",
        fbref_path_name="Bukayo-Saka",
        client=client,
    )
    with respx.mock:
        fusion = await member.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert fusion.fotmob.name == "Bukayo Saka"
