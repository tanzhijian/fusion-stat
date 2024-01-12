import typing

import httpx
import pytest

from fusion_stat.spiders.serie_a import Competition
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Serie A", season=2023, client=client)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://www.legaseriea.it/api/stats/Classificacompleta?CAMPIONATO=A&STAGIONE=2023-24&TURNO=UNICO&GIRONE=UNI"
        )

    def test_parse(self, spider: Competition) -> None:
        data = read_data("serie_a", "STAGIONE=2023-24.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com["id"] == "Serie A 2023-24"
        team = com["teams"][2]
        assert team["id"] == "milan"
        assert team["name"] == "Milan"
        assert team["country_code"] == "ITA"
        assert (
            team["logo"]
            == "https://img.legaseriea.it/vimages/62cef513/milan.png"
        )
