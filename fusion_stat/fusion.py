import asyncio
import typing

from .base import Downloader
from .models.competition import Competition
from .models.competitions import Competitions
from .models.match import Match
from .models.matches import Matches
from .models.member import Member
from .models.team import Team
from .spiders.fbref import Competition as FBrefCompetition
from .spiders.fbref import Competitions as FBrefCompetitions
from .spiders.fbref import Match as FBrefMatch
from .spiders.fbref import Matches as FBrefMatches
from .spiders.fbref import Member as FBrefMember
from .spiders.fbref import Team as FBrefTeam
from .spiders.fotmob import Competition as FotMobCompetition
from .spiders.fotmob import Competitions as FotMobCompetitions
from .spiders.fotmob import Match as FotMobMatch
from .spiders.fotmob import Matches as FotMobMatches
from .spiders.fotmob import Member as FotMobMember
from .spiders.fotmob import Team as FotMobTeam
from .spiders.official import Competition as OfficialCompetition


class Fusion(Downloader):
    async def gather(
        self,
        tasks: tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...],
    ) -> list[typing.Any]:
        result = await asyncio.gather(*tasks)
        return result

    async def get_competitions(self, season: int | None = None) -> Competitions:
        tasks = (
            FotMobCompetitions(client=self.client).process(),
            FBrefCompetitions(client=self.client).process(),
        )
        fotmob, fbref = await self.gather(tasks)
        return Competitions(fotmob=fotmob, fbref=fbref, season=season)

    async def get_competition(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
        official_name: str,
        season: int | None = None,
    ) -> Competition:
        tasks = (
            FotMobCompetition(
                id=fotmob_id,
                season=season,
                client=self.client,
            ).process(),
            FBrefCompetition(
                id=fbref_id,
                path_name=fbref_path_name,
                season=season,
                client=self.client,
            ).process(),
            OfficialCompetition(
                name=official_name,
                season=season,
                client=self.client,
            ).process(),
        )
        fotmob, fbref, official = await self.gather(tasks)
        return Competition(fotmob=fotmob, fbref=fbref, official=official)

    async def get_team(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
    ) -> Team:
        tasks = (
            FotMobTeam(id=fotmob_id, client=self.client).process(),
            FBrefTeam(
                id=fbref_id, path_name=fbref_path_name, client=self.client
            ).process(),
        )
        fotmob, fbref = await self.gather(tasks)
        return Team(fotmob=fotmob, fbref=fbref)

    async def get_member(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
    ) -> Member:
        tasks = (
            FotMobMember(id=fotmob_id, client=self.client).process(),
            FBrefMember(
                id=fbref_id,
                path_name=fbref_path_name,
                client=self.client,
            ).process(),
        )
        fotmob, fbref = await self.gather(tasks)
        return Member(fotmob=fotmob, fbref=fbref)

    async def get_matches(self, *, date: str) -> Matches:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        tasks = (
            FotMobMatches(date=date, client=self.client).process(),
            FBrefMatches(date=date, client=self.client).process(),
        )
        fotmob, fbref = await self.gather(tasks)
        return Matches(fotmob=fotmob, fbref=fbref)

    async def get_match(self, *, fotmob_id: str, fbref_id: str) -> Match:
        tasks = (
            FotMobMatch(id=fotmob_id, client=self.client).process(),
            FBrefMatch(id=fbref_id, client=self.client).process(),
        )
        fotmob, fbref = await self.gather(tasks)
        return Match(fotmob=fotmob, fbref=fbref)
