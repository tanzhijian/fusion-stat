import httpx
import pytest

from fusion_stat import Member
from fusion_stat.spiders import fbref, fotmob, transfermarkt
from tests.utils import read_data


class TestMember:
    @pytest.fixture(scope="class")
    def member(self) -> Member:
        fotmob_data = read_data("fotmob", "playerData?id=961995.json")
        fbref_data = read_data("fbref", "players_bc7dc64d_Bukayo-Saka.html")
        transfermarkt_data = read_data(
            "transfermarkt", "bukayo-saka_profil_spieler_433177.html"
        )

        fotmob_spider = fotmob.Member(id="961995")
        fbref_spider = fbref.Member(id="bc7dc64d")
        transfermarkt_spider = transfermarkt.Member(
            id="433177", path_name="bukayo-saka"
        )

        return Member(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
        )

    def test_info(self, member: Member) -> None:
        assert member.fotmob["name"] == "Bukayo Saka"
