import typing
from pathlib import Path

import httpx
import pytest
import respx

from fusion_stat.spiders.fbref import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)


def mock(file: str) -> None:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    respx.get(
        f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, text=text))


def read_text(file: str) -> str:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    return text


class TestCompetitions:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competitions, typing.Any, None]:
        yield Competitions(client=client)

    def test_request(self, spider: Competitions) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/comps/"

    def test_parse(self, spider: Competitions) -> None:
        text = read_text("comps_.html")
        response = httpx.Response(200, text=text)
        coms = spider.parse(response)
        assert coms[0].name == "Premier League"


class TestCompetition:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Competition, typing.Any, None]:
        yield Competition(id="9", path_name="Premier-League", client=client)

    def test_request(
        self, spider: Competition, client: httpx.AsyncClient
    ) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/comps/9/Premier-League-Stats"

        for url2, spider2 in zip(
            (
                "https://fbref.com/en/comps/9",
                "https://fbref.com/en/comps/9/2022-2023",
                (
                    "https://fbref.com/en/comps/9/2022-2023/"
                    "2022-2023-Premier-League-Stats"
                ),
            ),
            (
                Competition(id="9", client=client),
                Competition(id="9", season="2022-2023", client=client),
                Competition(
                    id="9",
                    season="2022-2023",
                    path_name="Premier-League",
                    client=client,
                ),
            ),
        ):
            assert url2 == spider2.request.url

    def test_parse(self, spider: Competition) -> None:
        text = read_text("comps_9_Premier-League-Stats.html")
        response = httpx.Response(200, text=text)
        com = spider.parse(response)
        assert com.name == "Premier League"


class TestTeam:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Team, typing.Any, None]:
        yield Team(id="18bb7c10", path_name="Arsenal", client=client)

    def test_request(self, spider: Team, client: httpx.AsyncClient) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"

        for url2, spider2 in zip(
            (
                "https://fbref.com/en/squads/18bb7c10",
                "https://fbref.com/en/squads/18bb7c10/2022-2023",
                "https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats",
            ),
            (
                Team(id="18bb7c10", client=client),
                Team(id="18bb7c10", season="2022-2023", client=client),
                Team(
                    id="18bb7c10",
                    path_name="Arsenal",
                    season="2022-2023",
                    client=client,
                ),
            ),
        ):
            assert url2 == spider2.request.url

    def test_parse(self, spider: Team) -> None:
        text = read_text("squads_18bb7c10_Arsenal-Stats.html")
        response = httpx.Response(200, text=text)
        team = spider.parse(response)
        assert team.name == "Arsenal"
        assert int(team.shooting.xg) == int(8.3)


class TestMember:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Member, typing.Any, None]:
        yield Member(id="bc7dc64d", path_name="Bukayo-Saka", client=client)

    def test_request(self, spider: Member, client: httpx.AsyncClient) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/players/bc7dc64d/Bukayo-Saka"

        spider2 = Member(id="bc7dc64d", client=client)
        assert spider2.request.url == "https://fbref.com/en/players/bc7dc64d/"

    def test_parse(self, spider: Member) -> None:
        text = read_text("players_bc7dc64d_Bukayo-Saka.html")
        response = httpx.Response(200, text=text)
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
        assert url == "https://fbref.com/en/matches/2023-09-03"

    def test_parse(self, spider: Matches) -> None:
        text = read_text("matches_2023-09-03.html")
        response = httpx.Response(200, text=text)
        matches = spider.parse(response)
        match = matches[0]
        assert match.id == "bdbc722e"
        assert match.name == "Liverpool vs Aston Villa"


class TestMatch:
    @pytest.fixture(scope="class")
    def spider(
        self, client: httpx.AsyncClient
    ) -> typing.Generator[Match, typing.Any, None]:
        yield Match(id="74125d47", client=client)

    def test_request(self, spider: Match) -> None:
        url = spider.request.url
        assert url == "https://fbref.com/en/matches/74125d47"

    def test_parse(self, spider: Match) -> None:
        text = read_text("matches_74125d47.html")
        response = httpx.Response(200, text=text)
        match = spider.parse(response)
        assert match.name == "Arsenal vs Manchester United"
