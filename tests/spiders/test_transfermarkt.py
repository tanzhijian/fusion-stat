import typing

import httpx
import pytest

from fusion_stat.spiders.transfermarkt import Competition, Competitions

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


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="GB1", path_name="premier-league", client=client)

    def test_request(self, spider: Competition) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"
        )

    def test_request_include_season(self, spider: Competition) -> None:
        spider.season = 2021
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2021"
        )

    def test_parse(self, spider: Competition) -> None:
        text = read_data(
            "transfermarkt", "premier-league_startseite_wettbewerb_GB1.html"
        )
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com["id"] == "GB1"
        assert com["name"] == "Premier League"
        assert len(com["teams"]) == 20

        team = com["teams"][0]
        assert team["id"] == "281"
        assert team["name"] == "Manchester City"
        assert team["total_market_value"] == "€1.29bn"