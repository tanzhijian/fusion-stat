import httpx
import pytest

from fusion_stat import Member
from fusion_stat.spiders import fbref, fotmob
from tests.utils import read_data


class TestMember:
    @pytest.fixture(scope="class")
    def member(self, client: httpx.AsyncClient) -> Member:
        fotmob_data = read_data("fotmob", "playerData?id=961995.json")
        fbref_data = read_data("fbref", "players_bc7dc64d_Bukayo-Saka.html")

        fotmob_spider = fotmob.Member(id="961995", client=client)
        fbref_spider = fbref.Member(id="bc7dc64d", client=client)

        return Member(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_info(self, member: Member) -> None:
        assert member.fotmob["name"] == "Bukayo Saka"
