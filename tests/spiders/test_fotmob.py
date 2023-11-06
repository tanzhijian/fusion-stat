import typing
from functools import partial

import httpx
import pytest

from tests.utils import read_data
from fusion_stat.spiders.fotmob import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)


read_test_data = partial(read_data, "fotmob")


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions(client=client)

    def test_request(self, spider: Competitions) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/allLeagues"

    def test_parse(self, spider: Competitions) -> None:
        data = read_test_data("allLeagues.json")
        response = httpx.Response(200, json=data)
        coms = spider.parse(response)
        assert coms[0].name == "Premier League"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="47", client=client)

    def test_request(self, spider: Competition) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/leagues?id=47"

    def test_parse(self, spider: Competition) -> None:
        data = read_test_data("leagues?id=47.json")
        response = httpx.Response(200, json=data)
        com = spider.parse(response)
        assert com.name == "Premier League"


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Team, typing.Any, None]:
        yield Team(id="9825", client=client)

    def test_request(self, spider: Team) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/teams?id=9825"

    def test_parse(self, spider: Team) -> None:
        data = read_test_data("teams?id=9825.json")
        response = httpx.Response(200, json=data)
        team = spider.parse(response)
        assert team.name == "Arsenal"


class TestMember:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Member, typing.Any, None]:
        yield Member(id="961995", client=client)

    def test_request(self, spider: Member) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/playerData?id=961995"

    def test_parse(self, spider: Member) -> None:
        data = read_test_data("playerData?id=961995.json")
        response = httpx.Response(200, json=data)
        member = spider.parse(response)
        assert member.name == "Bukayo Saka"


class TestMatches:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Matches, typing.Any, None]:
        yield Matches(date="2023-09-03", client=client)

    def test_request(self, spider: Matches) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/matches?date=20230903"

    def test_parse(self, spider: Matches) -> None:
        data = read_test_data("matches?date=20230903.json")
        response = httpx.Response(200, json=data)
        matches = spider.parse(response)
        match = matches[0]
        assert match.id == "4193495"
        assert match.name == "Crystal Palace vs Wolverhampton Wanderers"


class TestMatch:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Match, typing.Any, None]:
        yield Match(id="4193490", client=client)

    def test_request(self, spider: Match) -> None:
        url = spider.request.url
        assert url == "https://www.fotmob.com/api/matchDetails?matchId=4193490"

    def test_parse(self, spider: Match) -> None:
        data = read_test_data("matchDetails?matchId=4193490.json")
        response = httpx.Response(200, json=data)
        match = spider.parse(response)
        assert match.name == "Arsenal vs Manchester United"