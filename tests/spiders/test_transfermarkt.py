import typing

import httpx
import pytest

from fusion_stat.spiders.transfermarkt import Competitions

from ..utils import read_data


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions(client=client)

    def test_request(self, spider: Competitions) -> None:
        url = spider.request.url
        assert url == "https://www.transfermarkt.com/wettbewerbe/europa"

    def test_parse(self, spider: Competitions) -> None:
        text = read_data("transfermarkt", "wettbewerbe_europa.html")
        response = httpx.Response(200, text=text)
        coms = spider.parse(response)
        com = coms[0]
        assert com["id"] == "GB1"
        assert com["name"] == "Premier League"
