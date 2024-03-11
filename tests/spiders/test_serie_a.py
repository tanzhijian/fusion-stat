import httpx
import pytest

from fusion_stat.spiders import official
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> official.competition.Spider:
        return official.competition.Spider(name="Serie A", season=2023)

    def test_request(self, spider: official.competition.Spider) -> None:
        assert (
            spider.request.url
            == "https://www.legaseriea.it/api/stats/Classificacompleta?CAMPIONATO=A&STAGIONE=2023-24&TURNO=UNICO&GIRONE=UNI"
        )

    def test_parse(self, spider: official.competition.Spider) -> None:
        data = read_data("serie_a", "STAGIONE=2023-24.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.id == "Serie A 2023-24"
        team = com.teams[2]
        assert team.id == "milan"
        assert team.name == "Milan"
        assert team.country_code == "ITA"
        assert (
            team.logo == "https://img.legaseriea.it/vimages/62cef513/milan.png"
        )
