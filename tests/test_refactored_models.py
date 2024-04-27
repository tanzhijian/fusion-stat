import pytest

from fusion_stat.refactored_models import (
    Competition,
    Match,
    Player,
    Staff,
    Team,
)


class TestCompetition:
    @pytest.fixture(scope="class")
    def foo_com(self) -> Competition:
        teams = [
            Team(
                id="ARS",
                name="Arsenal",
                country_code="ENG",
                items={"foo": "foo"},
            ),
            Team(
                id="MCI",
                name="Man City",
                country_code="ENG",
                items={"foo": "foo"},
            ),
        ]

        competition = Competition(
            id="PL", name="Premier League", country_code="ENG", season=2023
        )
        home = Team(id="ARS", name="Arsenal", country_code="ENG")
        away = Team(id="MCI", name="Man City", country_code="ENG")
        matches = [
            Match(
                id="1",
                name="Arsenal vs Man City",
                date="2023-04-27",
                competition=competition,
                home=home,
                away=away,
            )
        ]
        return Competition(
            id="PL",
            name="Premier League",
            country_code="ENG",
            season=2023,
            items={"foo": "foo"},
            teams=teams,
            matches=matches,
        )

    @pytest.fixture(scope="class")
    def bar_com(self) -> Competition:
        teams = [
            Team(
                id="1",
                name="Arsenal",
                country_code="ENG",
                items={"bar": 10},
            ),
            Team(
                id="2",
                name="Manchester City",
                country_code="ENG",
                items={"foo": 10},
            ),
        ]

        competition = Competition(
            id="9", name="Premier League", country_code="ENG", season=2023
        )
        home = Team(id="1", name="Arsenal", country_code="ENG")
        away = Team(id="2", name="Manchester City", country_code="ENG")
        matches = [
            Match(
                id="2nd",
                name="Manchester City vs Arsenal",
                date="2023-04-27",
                competition=competition,
                home=home,
                away=away,
            )
        ]
        return Competition(
            id="9",
            name="Premier League",
            country_code="ENG",
            season=2023,
            items={"bar": 10},
            teams=teams,
            matches=matches,
        )

    def test_attrs(self, foo_com: Competition) -> None:
        assert foo_com.id == "PL"

        if foo_com.teams:
            team = foo_com.teams[0]
            assert team.name == "Arsenal"

        if foo_com.matches:
            match = foo_com.matches[0]
            assert match.competition.id == "PL"
            assert match.home.id == "ARS"
            assert match.away.id == "MCI"

    def test_add(self, foo_com: Competition, bar_com: Competition) -> None:
        com = foo_com.add(bar_com)
        assert com.id == "PL"
        assert com.items["foo"] == "foo"
        assert com.items["bar"] == 10

        if com.teams:
            team = com.teams[0]
            assert team.id == "ARS"
            assert team.items["foo"] == "foo"
            assert team.items["bar"] == 10

        if com.matches:
            match = com.matches[0]
            assert match.competition.id == "PL"
            assert match.home.id == "ARS"
            assert match.away.id == "MCI"


class TestTeam:
    @pytest.fixture(scope="class")
    def foo_team(self) -> Team:
        staffs = [
            Staff(
                id="1",
                name="Arteta",
                country_code="ESP",
                position="Manager",
                items={"foo": "foo"},
            )
        ]
        players = [
            Player(
                id="2",
                name="Saka",
                country_code="ENG",
                position="FW",
                items={"foo": "foo"},
            )
        ]
        return Team(
            id="3",
            name="Arsenal",
            country_code="ENG",
            items={"foo": "foo"},
            staffs=staffs,
            players=players,
        )

    @pytest.fixture(scope="class")
    def bar_team(self) -> Team:
        staffs = [
            Staff(
                id="a",
                name="Mikel Arteta",
                country_code="ESP",
                position="Manager",
                items={"bar": 10},
            )
        ]
        players = [
            Player(
                id="b",
                name="Bukayo Saka",
                country_code="ENG",
                position="FW",
                items={"bar": 10},
            )
        ]
        return Team(
            id="c",
            name="Arsenal FC",
            country_code="ENG",
            items={"bar": 10},
            staffs=staffs,
            players=players,
        )

    def test_attrs(self, foo_team: Team) -> None:
        assert foo_team.id == "3"
        assert foo_team.name == "Arsenal"
        assert foo_team.country_code == "ENG"

        if foo_team.staffs:
            staff = foo_team.staffs[0]
            assert staff.name == "Arteta"
            assert staff.position == "Manager"

        if foo_team.players:
            player = foo_team.players[0]
            assert player.name == "Saka"
            assert player.position == "FW"

    def add(self, foo_team: Team, bar_team: Team) -> None:
        team = foo_team.add(bar_team)
        assert team.id == "3"
        assert team.name == "Arsenal"
        assert team.country_code == "ENG"
        assert team.items["foo"] == "foo"
        assert team.items["bar"] == 10

        if team.staffs:
            staff = team.staffs[0]
            assert staff.name == "Arteta"
            assert staff.position == "Manager"
            assert staff.items["foo"] == "foo"
            assert staff.items["bar"] == 10

        if team.players:
            player = team.players[0]
            assert player.name == "Saka"
            assert player.position == "FW"
            assert player.items["foo"] == "foo"
            assert player.items["bar"] == 10


class TestMatch:
    @pytest.fixture(scope="class")
    def foo_match(self) -> Match:
        competition = Competition(
            id="PL", name="Premier League", country_code="ENG", season=2023
        )
        home = Team(id="ARS", name="Arsenal", country_code="ENG")
        away = Team(id="MCI", name="Man City", country_code="ENG")
        return Match(
            id="1",
            name="Arsenal vs Man City",
            items={"foo": "foo"},
            date="2024-04-27",
            competition=competition,
            home=home,
            away=away,
        )

    @pytest.fixture(scope="class")
    def bar_match(self) -> Match:
        competition = Competition(
            id="9", name="Premier League", country_code="ENG", season=2023
        )
        home = Team(id="1", name="Arsenal", country_code="ENG")
        away = Team(id="2", name="Manchester City", country_code="ENG")
        return Match(
            id="2nd",
            name="Manchester City vs Arsenal",
            items={"bar": 10},
            date="2024-04-27",
            competition=competition,
            home=home,
            away=away,
        )

    def test_attrs(self, foo_match: Match) -> None:
        assert foo_match.id == "1"
        assert foo_match.competition.id == "PL"
        assert foo_match.home.id == "ARS"
        assert foo_match.away.id == "MCI"

    def test_add(self, foo_match: Match, bar_match: Match) -> None:
        match = foo_match.add(bar_match)
        assert match.id == "1"
        assert match.competition.id == "PL"
        assert match.home.id == "ARS"
        assert match.away.id == "MCI"
        assert match.items["foo"] == "foo"
        assert match.items["bar"] == 10
