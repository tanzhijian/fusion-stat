import httpx
import pytest

from fusion_stat import Player
from fusion_stat.spiders import fbref, fotmob, transfermarkt
from tests.utils import read_data


class TestPlayer:
    @pytest.fixture(scope="class")
    def player(self) -> Player:
        fotmob_data = read_data("fotmob", "playerData?id=961995.json")
        fbref_data = read_data("fbref", "players_bc7dc64d_Bukayo-Saka.html")
        transfermarkt_data = read_data(
            "transfermarkt", "bukayo-saka_profil_spieler_433177.html"
        )

        fotmob_spider = fotmob.player.Spider(id="961995")
        fbref_spider = fbref.player.Spider(id="bc7dc64d")
        transfermarkt_spider = transfermarkt.player.Spider(
            id="433177", path_name="bukayo-saka"
        )

        return Player(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
            transfermarkt=transfermarkt_spider.parse(
                httpx.Response(200, text=transfermarkt_data)
            ),
        )
