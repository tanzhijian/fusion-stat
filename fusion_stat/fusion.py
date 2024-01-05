import asyncio
import typing

from .base import Downloader
from .config import COMPETITIONS
from .models import StatDict
from .models.competition import Competition
from .models.competitions import Competitions
from .models.match import Match
from .models.matches import Matches
from .models.member import Member
from .models.team import Team
from .spiders import fbref, fotmob, official


class Fusion(Downloader):
    async def gather(
        self,
        tasks: tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...],
    ) -> list[typing.Any]:
        result = await asyncio.gather(*tasks)
        return result

    async def get_competitions(self, season: int | None = None) -> Competitions:
        tasks = (
            fotmob.Competitions(client=self.client).process(),
            fbref.Competitions(client=self.client).process(),
        )
        fotmob_competitions, fbref_competitions = await self.gather(tasks)
        return Competitions(
            fotmob=fotmob_competitions, fbref=fbref_competitions, season=season
        )

    def get_competitions_cache(self, season: int | None = None) -> Competitions:
        fotmob_competitions: list[StatDict] = []
        fbref_competitions: list[StatDict] = []
        for name, competition in COMPETITIONS.items():
            fotmob_competitions.append(
                StatDict(
                    id=competition["fotmob_id"],
                    name=name,
                    # 这里有个问题是fotmob.Competitions 使用的是 fotmob.name,
                    # 而现在使用的是 config.key,
                    # 需要保证之后的 config.key 和 fotmob.name 都要一致，或者之后修正
                )
            )

            if (fbref_path_name := competition["fbref_path_name"]) is None:
                raise ValueError("Config COMPETITIONS is not fbref_path_name")
            fbref_name = " ".join(fbref_path_name.split("-"))
            fbref_competitions.append(
                StatDict(
                    id=competition["fbref_id"],
                    name=fbref_name,
                )
            )
        return Competitions(
            fotmob=tuple(fotmob_competitions),
            fbref=tuple(fbref_competitions),
            season=season,
        )

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
            fotmob.Competition(
                id=fotmob_id,
                season=season,
                client=self.client,
            ).process(),
            fbref.Competition(
                id=fbref_id,
                path_name=fbref_path_name,
                season=season,
                client=self.client,
            ).process(),
            official.Competition(
                name=official_name,
                season=season,
                client=self.client,
            ).process(),
        )
        (
            fotmob_competition,
            fbref_competition,
            official_competition,
        ) = await self.gather(tasks)
        return Competition(
            fotmob=fotmob_competition,
            fbref=fbref_competition,
            official=official_competition,
        )

    async def get_team(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
    ) -> Team:
        tasks = (
            fotmob.Team(id=fotmob_id, client=self.client).process(),
            fbref.Team(
                id=fbref_id, path_name=fbref_path_name, client=self.client
            ).process(),
        )
        fotmob_team, fbref_team = await self.gather(tasks)
        return Team(fotmob=fotmob_team, fbref=fbref_team)

    async def get_member(
        self,
        *,
        fotmob_id: str,
        fbref_id: str,
        fbref_path_name: str | None = None,
    ) -> Member:
        tasks = (
            fotmob.Member(id=fotmob_id, client=self.client).process(),
            fbref.Member(
                id=fbref_id,
                path_name=fbref_path_name,
                client=self.client,
            ).process(),
        )
        fotmob_member, fbref_member = await self.gather(tasks)
        return Member(fotmob=fotmob_member, fbref=fbref_member)

    async def get_matches(self, *, date: str) -> Matches:
        """Parameters:

        * date: "%Y-%m-%d", such as "2023-09-03"
        """
        tasks = (
            fotmob.Matches(date=date, client=self.client).process(),
            fbref.Matches(date=date, client=self.client).process(),
        )
        fotmob_matches, fbref_matches = await self.gather(tasks)
        return Matches(fotmob=fotmob_matches, fbref=fbref_matches)

    async def get_match(self, *, fotmob_id: str, fbref_id: str) -> Match:
        tasks = (
            fotmob.Match(id=fotmob_id, client=self.client).process(),
            fbref.Match(id=fbref_id, client=self.client).process(),
        )
        fotmob_match, fbref_match = await self.gather(tasks)
        return Match(fotmob=fotmob_match, fbref=fbref_match)
