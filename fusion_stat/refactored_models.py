import typing
from abc import ABC, abstractmethod

from rapidfuzz import process

from .config import MEMBERS_SCORE_CUFOFF
from .utils import mean_scorer


class _Base(ABC):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
    ) -> None:
        self.id = id
        self.name = name
        self.items = items

    @abstractmethod
    def add(self, new: typing.Any) -> typing.Any:
        ...


class Competition(_Base):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
        country_code: str,
        teams: typing.Sequence["Team"] | None = None,
        matches: typing.Sequence["Match"] | None = None,
    ) -> None:
        super().__init__(id=id, name=name, items=items)
        self.country_code = country_code
        self.teams = teams
        self.matches = matches

    def add(self, new: "Competition") -> "Competition":
        items = self.items | new.items

        if new.teams is not None and self.teams is not None:
            teams = self._concat_teams(new.teams)
        elif self.teams is None:
            teams = new.teams
        else:
            teams = self.teams

        if new.matches is not None and self.matches is not None:
            matches = self._concat_matches(new.matches)
        elif self.matches is None:
            matches = new.matches
        else:
            matches = self.matches

        return Competition(
            id=self.id,
            name=self.name,
            items=items,
            country_code=self.country_code,
            teams=teams,
            matches=matches,
        )

    def _concat_teams(self, teams: typing.Sequence["Team"]) -> list["Team"]:
        if self.teams is None or teams is None:
            raise ValueError("Teams is None")

        results: list["Team"] = []
        for query in self.teams:
            selected = process.extractOne(
                query,
                teams,
                processor=lambda x: x.name,
            )
            result = selected[0]
            results.append(query.add(result))

        return results

    def _concat_matches(
        self, matches: typing.Sequence["Match"]
    ) -> list["Match"]:
        if self.matches is None or matches is None:
            raise ValueError("Matches is None")

        results: list["Match"] = []
        for query in self.matches:
            selected = process.extractOne(
                query,
                matches,
                processor=lambda x: x.name,
            )
            result = selected[0]
            results.append(query.add(result))

        return results


class Team(_Base):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
        country_code: str,
        players: typing.Sequence["Player"] | None = None,
        staffs: typing.Sequence["Staff"] | None = None,
    ) -> None:
        super().__init__(id=id, name=name, items=items)
        self.country_code = country_code
        self.players = players
        self.staffs = staffs

    def add(self, new: "Team") -> "Team":
        items = self.items | new.items

        if new.players is not None and self.players is not None:
            players = self._concat_players(new.players)
        elif self.players is None:
            players = new.players
        else:
            players = self.players

        if new.staffs is not None and self.staffs is not None:
            staffs = self._concat_staffs(new.staffs)
        elif self.staffs is None:
            staffs = new.staffs
        else:
            staffs = self.staffs

        return Team(
            id=self.id,
            name=self.name,
            items=items,
            country_code=self.country_code,
            players=players,
            staffs=staffs,
        )

    def _concat_players(
        self, players: typing.Sequence["Player"]
    ) -> list["Player"]:
        if self.players is None or players is None:
            raise ValueError("Players is None")

        results: list["Player"] = []
        for query in self.players:
            selected = process.extractOne(
                query,
                players,
                scorer=mean_scorer,
                processor=lambda x: [
                    x.name,
                    x.country_code,
                    x.position,
                ],
                score_cutoff=MEMBERS_SCORE_CUFOFF,
            )
            if selected is not None:
                result = selected[0]
                results.append(query.add(result))

        return results

    def _concat_staffs(self, staffs: typing.Sequence["Staff"]) -> list["Staff"]:
        if self.staffs is None or staffs is None:
            raise ValueError("Staffs is None")

        results: list["Staff"] = []
        for query in self.staffs:
            selected = process.extractOne(
                query,
                staffs,
                scorer=mean_scorer,
                processor=lambda x: [
                    x.name,
                    x.country_code,
                    x.position,
                ],
                score_cutoff=MEMBERS_SCORE_CUFOFF,
            )
            if selected is not None:
                result = selected[0]
                results.append(query.add(result))

        return results


class Staff(_Base):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
        country_code: str,
        position: str,
    ) -> None:
        super().__init__(id=id, name=name, items=items)
        self.country_code = country_code
        self.position = position

    def add(self, new: "Staff") -> "Staff":
        items = self.items | new.items
        return Staff(
            id=self.id,
            name=self.name,
            items=items,
            country_code=self.country_code,
            position=self.position,
        )


class Player(_Base):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
        country_code: str,
        position: str,
    ) -> None:
        super().__init__(id=id, name=name, items=items)
        self.country_code = country_code
        self.position = position

    def add(self, new: "Player") -> "Player":
        items = self.items | new.items
        return Player(
            id=self.id,
            name=self.name,
            items=items,
            country_code=self.country_code,
            position=self.position,
        )


class Match(_Base):
    def __init__(
        self,
        *,
        id: str,
        name: str,
        items: dict[str, typing.Any],
        competition: Competition,
        home: Team,
        away: Team,
    ) -> None:
        super().__init__(id=id, name=name, items=items)
        self.competition = competition
        self.home = home
        self.away = away

    def add(self, new: "Match") -> "Match":
        items = self.items | new.items
        return Match(
            id=self.id,
            name=self.name,
            items=items,
            competition=self.competition,
            home=self.home,
            away=self.away,
        )
