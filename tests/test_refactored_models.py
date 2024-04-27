import pytest

from fusion_stat.refactored_models import Competition, Match, Team


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

    def test_attr(self, foo_com: Competition) -> None:
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
