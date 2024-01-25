import typing
from types import TracebackType

import httpx

from .models import (
    Competition,
    Competitions,
    Match,
    Matches,
    Player,
    Staff,
    Team,
)
from .scraper import Engine
from .spiders import fbref, fotmob, official, transfermarkt

U = typing.TypeVar("U")


class Fusion:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.engine = Engine(client)

    async def close(self) -> None:
        await self.engine.close()

    async def __aenter__(self: U) -> U:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self.close()

    async def get_competitions(self, season: int | None = None) -> Competitions:
        spiders = (
            fotmob.Competitions(),
            fbref.Competitions(),
            transfermarkt.Competitions(),
        )
        (
            fotmob_competitions,
            fbref_competitions,
            transfermarkt_competitions,
        ) = await self.engine.process(*spiders)
        return Competitions(
            fotmob=fotmob_competitions,
            fbref=fbref_competitions,
            transfermarkt=transfermarkt_competitions,
            season=season,
        )

    async def get_competition(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        official_name: str,
        transfermarkt_id: str,
        transfermarkt_path_name: str,
        season: int | None = None,
    ) -> Competition:
        spiders = (
            fotmob.Competition(id=fotmob_id, season=season),
            fbref.Competition(
                id=fbref_id, path_name=fbref_path_name, season=season
            ),
            official.Competition(name=official_name, season=season),
            transfermarkt.Competition(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
        )
        (
            fotmob_competition,
            fbref_competition,
            official_competition,
            transfermarkt_competition,
        ) = await self.engine.process(*spiders)
        return Competition(
            fotmob=fotmob_competition,
            fbref=fbref_competition,
            official=official_competition,
            transfermarkt=transfermarkt_competition,
        )

    async def get_team(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        transfermarkt_id: str,
        transfermarkt_path_name: str,
    ) -> Team:
        spiders = (
            fotmob.Team(id=fotmob_id),
            fbref.Team(id=fbref_id, path_name=fbref_path_name),
            transfermarkt.Team(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
        )
        fotmob_team, fbref_team, transfermarkt_team = await self.engine.process(
            *spiders
        )
        return Team(
            fotmob=fotmob_team,
            fbref=fbref_team,
            transfermarkt=transfermarkt_team,
        )

    async def get_player(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        transfermarkt_id: str,
        transfermarkt_path_name: str,
    ) -> Player:
        spiders = (
            fotmob.Player(id=fotmob_id),
            fbref.Player(id=fbref_id, path_name=fbref_path_name),
            transfermarkt.Player(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
        )
        (
            fotmob_member,
            fbref_member,
            transfermarkt_member,
        ) = await self.engine.process(*spiders)
        return Player(
            fotmob=fotmob_member,
            fbref=fbref_member,
            transfermarkt=transfermarkt_member,
        )

    async def get_staff(self) -> Staff:
        return Staff()

    async def get_matches(self, *, date: str) -> Matches:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        spiders = (
            fotmob.Matches(date=date),
            fbref.Matches(date=date),
        )
        fotmob_matches, fbref_matches = await self.engine.process(*spiders)
        return Matches(fotmob=fotmob_matches, fbref=fbref_matches)

    async def get_match(self, *, fotmob_id: str, fbref_id: str) -> Match:
        spiders = (
            fotmob.Match(id=fotmob_id),
            fbref.Match(id=fbref_id),
        )
        fotmob_match, fbref_match = await self.engine.process(*spiders)
        return Match(fotmob=fotmob_match, fbref=fbref_match)
