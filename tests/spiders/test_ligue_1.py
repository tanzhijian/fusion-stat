import typing

import httpx
import pytest

from fusion_stat.spiders.ligue_1 import Competition
from tests.utils import read_data


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Ligue 1", season=2023, client=client)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://www.ligue1.com/clubs/List?seasonId=2023-2024"
        )

    def test_parse(self, spider: Competition) -> None:
        text = read_data("ligue_1", "clubs_List?seasonId=2023-2024.html")
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com["id"] == "Ligue 1 2023-2024"
        team = com["teams"][11]
        assert team["id"] == "paris-saint-germain"
        assert team["name"] == "Paris Saint-Germain"
        assert (
            team["logo"]
            == "https://www.ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2023-2024/13.png"
        )

        rennes = com["teams"][-2]
        assert rennes["id"] == "stade-rennais-fc"
        assert rennes["name"] == "Rennes"
