import typing

import httpx
import pytest

from fusion_stat.spiders.wikipedia import Competition, Image
from tests.utils import read_wikipedia_test_data


class TestImage:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Image, typing.Any, None]:
        yield Image(id="Arsenal_F.C.", client=client)

    def test_request(self, spider: Image) -> None:
        url = spider.request.url
        assert (
            url
            == "https://en.wikipedia.org/api/rest_v1/page/summary/Arsenal_F.C."
        )

    def test_parse(self, spider: Image) -> None:
        data = read_wikipedia_test_data("summary|Arsenal_F.C.json")
        response = httpx.Response(200, json=data)
        image_url = spider.parse(response)
        assert (
            image_url
            == "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/292px-Arsenal_FC.svg.png"
        )


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="Premier_League", client=client)

    def test_request(self, spider: Competition) -> None:
        url = spider.request.url
        assert (
            url
            == "https://en.wikipedia.org/api/rest_v1/page/mobile-html/2023-24_Premier_League"
        )

    def test_parse(self, spider: Competition) -> None:
        response = httpx.Response(200, text="halo")
        com = spider.parse(response)
        assert com == "competition"
