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


class App:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._engine = Engine(client)

    async def close(self) -> None:
        await self._engine.close()

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
            fotmob.competitions.Spider(),
            fbref.competitions.Spider(),
            transfermarkt.competitions.Spider(),
        )
        (
            fotmob_competitions,
            fbref_competitions,
            transfermarkt_competitions,
        ) = await self._engine.process(*spiders)
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
            fotmob.competition.Spider(id=fotmob_id, season=season),
            fbref.competition.Spider(
                id=fbref_id, path_name=fbref_path_name, season=season
            ),
            official.competition.Spider(name=official_name, season=season),
            transfermarkt.competition.Spider(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
        )
        (
            fotmob_competition,
            fbref_competition,
            official_competition,
            transfermarkt_competition,
        ) = await self._engine.process(*spiders)
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
            fotmob.team.Spider(id=fotmob_id),
            fbref.team.Spider(id=fbref_id, path_name=fbref_path_name),
            transfermarkt.team.Spider(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
            transfermarkt.staffs.Spider(id=transfermarkt_id),
        )
        (
            fotmob_team,
            fbref_team,
            transfermarkt_team,
            transfermarkt_staffs,
        ) = await self._engine.process(*spiders)
        return Team(
            fotmob=fotmob_team,
            fbref=fbref_team,
            transfermarkt=transfermarkt_team,
            transfermarkt_staffs=transfermarkt_staffs,
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
            fotmob.player.Spider(id=fotmob_id),
            fbref.player.Spider(id=fbref_id, path_name=fbref_path_name),
            transfermarkt.player.Spider(
                id=transfermarkt_id, path_name=transfermarkt_path_name
            ),
        )
        (
            fotmob_player,
            fbref_player,
            transfermarkt_player,
        ) = await self._engine.process(*spiders)
        return Player(
            fotmob=fotmob_player,
            fbref=fbref_player,
            transfermarkt=transfermarkt_player,
        )

    async def get_staff(
        self,
        *,
        transfermarkt_id: str,
        transfermarkt_path_name: str,
    ) -> Staff:
        spiders = (
            transfermarkt.staff.Spider(
                id=transfermarkt_id,
                path_name=transfermarkt_path_name,
            ),
        )
        (transfermarkt_staff,) = await self._engine.process(*spiders)
        return Staff(transfermarkt=transfermarkt_staff)

    async def get_matches(self, *, date: str) -> Matches:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        spiders = (fotmob.matches.Spider(date=date),)
        (fotmob_matches,) = await self._engine.process(*spiders)
        return Matches(fotmob=fotmob_matches)

    async def get_match(self, *, fotmob_id: str) -> Match:
        spiders = (fotmob.match.Spider(id=fotmob_id),)
        (fotmob_match,) = await self._engine.process(*spiders)
        return Match(fotmob=fotmob_match)
