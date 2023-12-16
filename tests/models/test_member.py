import typing

import httpx
import pytest_asyncio
import respx

from fusion_stat import Fusion, Member
from tests.utils import fbref_mock, fotmob_mock


class TestMember:
    @pytest_asyncio.fixture(scope="class")
    async def member(
        self,
        client: httpx.AsyncClient,
    ) -> typing.AsyncGenerator[Member, typing.Any]:
        fotmob_mock("playerData?id=961995.json")
        fbref_mock("players_bc7dc64d_Bukayo-Saka.html")

        fusion = Fusion(client=client)
        with respx.mock:
            member = await fusion.get_member(
                fotmob_id="961995",
                fbref_id="bc7dc64d",
                fbref_path_name="Bukayo-Saka",
            )
        yield member

    def test_get(self, member: Member) -> None:
        assert member.fotmob.name == "Bukayo Saka"
