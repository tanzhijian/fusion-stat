import typing

import httpx
import pytest

from fusion_stat.spiders.wikipedia import Competition


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="Premier_League", client=client)

    def test_request(self, spider: Competition) -> None:
        url = spider.request.url
        assert url == "https://en.wikipedia.org/wiki/2023-24_Premier_League"

    def test_parse(self, spider: Competition) -> None:
        response = httpx.Response(200, text="halo")
        com = spider.parse(response)
        assert com == "competition"
