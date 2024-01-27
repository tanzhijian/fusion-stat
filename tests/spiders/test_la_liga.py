import httpx
import pytest

from fusion_stat.spiders.la_liga import Competition
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> Competition:
        return Competition(name="La Liga", season=2023)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://apim.laliga.com/public-service/api/v1/teams?subscriptionSlug=laliga-easports-2023&limit=99&offset=0&orderField=nickname&orderType=ASC"
        )

        com_2013 = Competition(name="La Liga", season=2013)
        assert (
            com_2013.request.url
            == "https://apim.laliga.com/public-service/api/v1/teams?subscriptionSlug=laliga-santander-2013&limit=99&offset=0&orderField=nickname&orderType=ASC"
        )

    def test_parse(self, spider: Competition) -> None:
        data = read_data(
            "la_liga", "subscriptionSlug=laliga-easports-2023.json"
        )
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com["id"] == "laliga-easports-2023"
        assert com["name"] == "La Liga"
        team = com["teams"][13]
        assert team["name"] == "Real Madrid"
        assert team["country_code"] == "ESP"
        assert (
            team["logo"]
            == "https://assets.laliga.com/assets/2019/06/07/small/real-madrid.png"
        )
