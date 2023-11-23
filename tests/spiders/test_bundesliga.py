import typing

import httpx
import pytest

from fusion_stat.spiders.bundesliga import Competition
from tests.utils import read_data


class TestCurrentCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Bundesliga", season=2023, client=client)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://www.bundesliga.com/en/bundesliga/clubs"
        )

    def test_parse(self, spider: Competition) -> None:
        text = read_data("bundesliga", "en_bundesliga_clubs.html")
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com.id == "Bundesliga 2023-2024"
        assert (
            com.logo
            == "https://www.bundesliga.com/assets/favicons/safari-pinned-tab_new.svg"
        )
        team = com.teams[0]
        assert team.id == "fc-bayern-muenchen"
        assert team.name == "FC Bayern München"
        assert (
            team.logo
            == "https://www.bundesliga.com/assets/clublogo/DFL-CLU-00000G.svg"
        )


class Test2022Competition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Bundesliga", season=2022, client=client)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://www.bundesliga.com/assets/historic-season/2022-2023.json"
        )

    def test_parse(self, spider: Competition) -> None:
        data = read_data("bundesliga", "assets_historic_season_2022-2023.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.id == "Bundesliga 2022-2023"
        team = com.teams[0]
        assert team.id == "fc-bayern-muenchen"
        assert team.name == "FC Bayern München"
        assert (
            team.logo
            == "https://www.bundesliga.com/assets/clublogo/DFL-CLU-00000G.svg"
        )


class Test2021Competition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(name="Bundesliga", season=2021, client=client)

    def test_request(self, spider: Competition) -> None:
        assert (
            spider.request.url
            == "https://www.bundesliga.com/assets/historic-season/2021-2022.json"
        )

    def test_parse(self, spider: Competition) -> None:
        data = read_data("bundesliga", "assets_historic_season_2021-2022.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.id == "Bundesliga 2021-2022"
        team = com.teams[0]
        assert team.id == "Bayern"
        assert team.name == "FC Bayern München"
        assert not team.logo
