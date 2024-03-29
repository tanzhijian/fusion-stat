import httpx
import pytest

from fusion_stat.spiders import transfermarkt
from fusion_stat.spiders.transfermarkt._common import convert_date_format

from ..utils import read_data


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.competitions.Spider:
        return transfermarkt.competitions.Spider()

    def test_request(self, spider: transfermarkt.competitions.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.transfermarkt.com/wettbewerbe/europa"

    def test_parse(self, spider: transfermarkt.competitions.Spider) -> None:
        text = read_data("transfermarkt", "wettbewerbe_europa.html")
        response = httpx.Response(200, text=text)
        coms = spider.parse(response)
        assert len(coms) == 5
        com = coms[0]
        assert com.id == "GB1"
        assert com.name == "Premier League"
        assert com.path_name == "premier-league"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.competition.Spider:
        return transfermarkt.competition.Spider(
            id="GB1", path_name="premier-league"
        )

    def test_request(self, spider: transfermarkt.competition.Spider) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"
        )

    def test_request_include_season(
        self, spider: transfermarkt.competition.Spider
    ) -> None:
        spider.season = 2021
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2021"
        )

    def test_parse(self, spider: transfermarkt.competition.Spider) -> None:
        text = read_data(
            "transfermarkt", "premier-league_startseite_wettbewerb_GB1.html"
        )
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com.id == "GB1"
        assert com.name == "Premier League"
        assert com.market_values == "€10.99bn"
        assert com.player_average_market_value == "€19.27m"
        assert len(com.teams) == 20

        team = com.teams[0]
        assert team.id == "281"
        assert team.name == "Manchester City"
        assert team.market_values == "€1.29bn"
        assert team.path_name == "manchester-city"

        assert com.teams[1].name == "Arsenal FC"


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.team.Spider:
        return transfermarkt.team.Spider(id="11", path_name="arsenal-fc")

    def test_request(self, spider: transfermarkt.team.Spider) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/arsenal-fc/startseite/verein/11"
        )

    def test_request_include_season(
        self, spider: transfermarkt.team.Spider
    ) -> None:
        spider.season = 2021
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/arsenal-fc/startseite/verein/11/saison_id/2021"
        )

    def test_parse(self, spider: transfermarkt.team.Spider) -> None:
        text = read_data(
            "transfermarkt", "arsenal-fc_startseite_verein_11.html"
        )
        response = httpx.Response(200, text=text)
        team = spider.parse(response)
        assert team.id == "11"
        assert team.name == "Arsenal FC"
        assert len(team.players) == 26

        player = team.players[0]
        assert player.id == "262749"
        assert player.name == "David Raya"
        assert player.date_of_birth == "1995-09-15"
        assert player.market_values == "€35.00m"
        assert player.path_name == "david-raya"
        assert player.position == "GK"
        assert player.country_code == "ESP"


class TestStaffs:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.staffs.Spider:
        return transfermarkt.staffs.Spider(id="11")

    def test_request(self, spider: transfermarkt.staffs.Spider) -> None:
        url = spider.request.url
        assert url == "https://www.transfermarkt.com/ceapi/staff/team/11/"

    def test_request_include_season(
        self, spider: transfermarkt.staffs.Spider
    ) -> None:
        spider.season = 2023
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/ceapi/staff/team/11/?saison_id=2023"
        )

    def test_parse(self, spider: transfermarkt.staffs.Spider) -> None:
        json = read_data("transfermarkt", "ceapi_staff_team_11_.json")
        response = httpx.Response(200, json=json)
        staffs = spider.parse(response)
        assert len(staffs) == 54
        staff = staffs[0]
        assert staff.id == "47620"
        assert staff.name == "Mikel Arteta"
        assert staff.position == "Manager"
        assert staff.path_name == "mikel-arteta"


class TestPlayer:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.player.Spider:
        return transfermarkt.player.Spider(id="433177", path_name="bukayo-saka")

    def test_request(self, spider: transfermarkt.player.Spider) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/bukayo-saka/profil/spieler/433177"
        )

    def test_parse(self, spider: transfermarkt.player.Spider) -> None:
        text = read_data(
            "transfermarkt", "bukayo-saka_profil_spieler_433177.html"
        )
        response = httpx.Response(200, text=text)
        player = spider.parse(response)
        assert player.id == "433177"
        assert player.name == "Bukayo Saka"
        assert player.market_values == "€120.00m"


def test_convert_date_format() -> None:
    assert convert_date_format("Aug 17, 1993 (30)") == "1993-08-17"


class TestStaff:
    @pytest.fixture(scope="class")
    def spider(self) -> transfermarkt.staff.Spider:
        return transfermarkt.staff.Spider(id="47620", path_name="mikel-arteta")

    def test_request(self, spider: transfermarkt.staff.Spider) -> None:
        url = spider.request.url
        assert (
            url
            == "https://www.transfermarkt.com/mikel-arteta/profil/trainer/47620"
        )

    def test_parse(self, spider: transfermarkt.staff.Spider) -> None:
        text = read_data(
            "transfermarkt", "mikel-arteta_profil_trainer_47620.html"
        )
        response = httpx.Response(200, text=text)
        staff = spider.parse(response)
        assert staff.id == "47620"
        assert staff.name == "Mikel Arteta"
