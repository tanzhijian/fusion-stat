import typing

import httpx
import pytest

from fusion_stat.spiders.transfermarkt import (
    Competition,
    Competitions,
    Member,
    Team,
    _convert_date_format,
)

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
        assert len(coms) == 5
        com = coms[0]
        assert com["id"] == "GB1"
        assert com["name"] == "Premier League"
        assert com["path_name"] == "premier-league"


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
        assert team["path_name"] == "manchester-city"

        assert com["teams"][1]["name"] == "Arsenal FC"


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Team, typing.Any, None]:
        yield Team(id="11", path_name="arsenal-fc", client=client)

    def test_request(self, spider: Team) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/arsenal-fc/startseite/verein/11"
        )

    def test_request_include_season(self, spider: Team) -> None:
        spider.season = 2021
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/arsenal-fc/startseite/verein/11/saison_id/2021"
        )

    def test_parse(self, spider: Team) -> None:
        text = read_data(
            "transfermarkt", "arsenal-fc_startseite_verein_11.html"
        )
        response = httpx.Response(200, text=text)
        team = spider.parse(response)
        assert team["id"] == "11"
        assert team["name"] == "Arsenal FC"
        assert len(team["members"]) == 26

        member = team["members"][0]
        assert member["id"] == "262749"
        assert member["name"] == "David Raya"
        assert member["date_of_birth"] == "1995-09-15"
        assert member["market_values"] == "€35.00m"
        assert member["path_name"] == "david-raya"
        assert member["position"] == "GK"
        assert member["country_code"] == "ESP"


class TestMember:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Member, typing.Any, None]:
        yield Member(id="433177", path_name="bukayo-saka", client=client)

    def test_request(self, spider: Member) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/bukayo-saka/profil/spieler/433177"
        )

    def test_parse(self, spider: Member) -> None:
        text = read_data(
            "transfermarkt", "bukayo-saka_profil_spieler_433177.html"
        )
        response = httpx.Response(200, text=text)
        member = spider.parse(response)
        assert member["id"] == "433177"
        assert member["name"] == "Bukayo Saka"
        assert member["market_values"] == "€120.00m"


def test_convert_date_format() -> None:
    assert _convert_date_format("Aug 17, 1993 (30)") == "1993-08-17"
