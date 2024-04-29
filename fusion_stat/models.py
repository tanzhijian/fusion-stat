import typing

from rapidfuzz import process

from . import spiders
from .config import MEMBERS_SCORE_CUFOFF
from .scraper import BaseItem
from .utils import mean_scorer


class CompetitionItemTypes(typing.Protocol):
    name: str
    country_code: str


class PlayerItemTypes(typing.Protocol):
    name: str
    country_code: str
    position: str | None


T = typing.TypeVar("T", bound=BaseItem)
U = typing.TypeVar("U", bound=PlayerItemTypes)
E = typing.TypeVar("E", bound=CompetitionItemTypes)


class Competitions:
    def __init__(
        self,
        fotmob: list[spiders.fotmob.competitions.Item],
        fbref: list[spiders.fbref.competitions.Item],
        transfermarkt: list[spiders.transfermarkt.competitions.Item],
        season: int | None = None,
    ) -> None:
        self._fotmob = fotmob
        self._fbref = fbref
        self._transfermarkt = transfermarkt
        self._season = season

    def _find_competition(
        self,
        query: CompetitionItemTypes,
        choices: typing.Sequence[E],
    ) -> E:
        result = process.extractOne(
            query,
            choices,
            scorer=mean_scorer,
            processor=lambda x: [
                x.name,
                x.country_code,
            ],
        )[0]
        return result

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "count": len(self._fotmob),
            "names": [com.name for com in self._fotmob],
        }

    def get_items(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_competition in self._fotmob:
            fbref_competition = self._find_competition(
                fotmob_competition, self._fbref
            )
            transfermarkt_competition = self._find_competition(
                fotmob_competition, self._transfermarkt
            )

            item = {
                "id": fotmob_competition.id,
                "name": fotmob_competition.name,
                "fotmob": fotmob_competition.model_dump(),
                "fbref": fbref_competition.model_dump(),
                "transfermarkt": transfermarkt_competition.model_dump(),
            }
            yield item

    @property
    def items(self) -> list[dict[str, typing.Any]]:
        return list(self.get_items())

    def get_params(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for item in self.get_items():
            competition_params = {
                "fotmob_id": item["fotmob"]["id"],
                "fbref_id": item["fbref"]["id"],
                "fbref_path_name": item["fbref"]["path_name"],
                "official_name": item["name"],
                "transfermarkt_id": item["transfermarkt"]["id"],
                "transfermarkt_path_name": item["transfermarkt"]["path_name"],
            }

            if self._season is not None:
                competition_params["season"] = self._season

            yield competition_params


class Competition:
    def __init__(
        self,
        fotmob: spiders.fotmob.competition.Item,
        fbref: spiders.fbref.competition.Item,
        official: spiders.official.competition.Item,
        transfermarkt: spiders.transfermarkt.competition.Item,
    ) -> None:
        self._fotmob = fotmob
        self._fbref = fbref
        self._official = official
        self._transfermarkt = transfermarkt

    def _find_team(
        self,
        query: BaseItem,
        choices: typing.Sequence[T],
    ) -> T:
        team = process.extractOne(
            query,
            choices,
            processor=lambda x: x.name,
        )[0]
        return team

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "id": self._fotmob.id,
            "name": self._fotmob.name,
            "logo": self._official.logo,
            "type": self._fotmob.type,
            "season": self._fotmob.season,
            "country_code": self._fotmob.country_code,
            "names": self._fotmob.names | {self._fbref.name},
            "market_values": self._transfermarkt.market_values,
            "player_average_market_value": self._transfermarkt.player_average_market_value,  # noqa: E501
        }

    def get_teams(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_team in self._fotmob.teams:
            fbref_team = self._find_team(fotmob_team, self._fbref.teams)
            official_team = self._find_team(fotmob_team, self._official.teams)
            transfermarkt_team = self._find_team(
                fotmob_team, self._transfermarkt.teams
            )

            team = {
                **fotmob_team.model_dump(),
                "country_code": official_team.country_code,
                "market_values": transfermarkt_team.market_values,
                "logo": official_team.logo,
                "shooting": fbref_team.shooting.model_dump(),
            }
            team["names"] |= fbref_team.names

            yield team

    @property
    def teams(self) -> list[dict[str, typing.Any]]:
        return list(self.get_teams())

    def get_matches(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_match in self._fotmob.matches:
            home = fotmob_match.home
            away = fotmob_match.away
            competition = fotmob_match.competition

            match = {
                "id": fotmob_match.id,
                "name": fotmob_match.name,
                "utc_time": fotmob_match.utc_time,
                "finished": fotmob_match.finished,
                "started": fotmob_match.started,
                "cancelled": fotmob_match.cancelled,
                "competition": competition.model_dump(),
                "home": home.model_dump(),
                "away": away.model_dump(),
            }
            yield match

    @property
    def matches(self) -> list[dict[str, typing.Any]]:
        return list(self.get_matches())

    def get_teams_params(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_team in self._fotmob.teams:
            fbref_team = self._find_team(
                fotmob_team,
                self._fbref.teams,
            )
            transfermarkt_team = self._find_team(
                fotmob_team,
                self._transfermarkt.teams,
            )

            team_params = {
                "fotmob_id": fotmob_team.id,
                "fbref_id": fbref_team.id,
                "fbref_path_name": fbref_team.path_name,
                "transfermarkt_id": transfermarkt_team.id,
                "transfermarkt_path_name": transfermarkt_team.path_name,
            }
            yield team_params


class Team:
    def __init__(
        self,
        fotmob: spiders.fotmob.team.Item,
        fbref: spiders.fbref.team.Item,
        transfermarkt: spiders.transfermarkt.team.Item,
        transfermarkt_staffs: list[spiders.transfermarkt.staffs.Item],
    ) -> None:
        self._fotmob = fotmob
        self._fbref = fbref
        self._transfermarkt = transfermarkt
        self._transfermarkt_staffs = transfermarkt_staffs

    def _find_player(
        self,
        query: PlayerItemTypes,
        choices: typing.Sequence[U],
    ) -> U:
        result = process.extractOne(
            query,
            choices,
            scorer=mean_scorer,
            processor=lambda x: [
                x.name,
                x.country_code,
                x.position,
            ],
            score_cutoff=MEMBERS_SCORE_CUFOFF,
        )[0]
        return result

    @property
    def info(self) -> dict[str, typing.Any]:
        return {
            "id": self._fotmob.id,
            "name": self._fotmob.name,
            "names": self._fotmob.names | self._fbref.names,
            "country_code": self._fotmob.country_code,
            "market_values": self._transfermarkt.market_values,
        }

    def get_staffs(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for transfermarkt_staff in self._transfermarkt_staffs:
            yield {
                "id": transfermarkt_staff.id,
                "name": transfermarkt_staff.name,
                "position": transfermarkt_staff.position,
            }

    @property
    def staffs(self) -> list[dict[str, typing.Any]]:
        return list(self.get_staffs())

    def get_players(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_player in self._fotmob.players:
            try:
                fbref_player = self._find_player(
                    fotmob_player,
                    self._fbref.players,
                )
                transfermarkt_player = self._find_player(
                    fotmob_player,
                    self._transfermarkt.players,
                )

                name = fotmob_player.name
                shooting = fbref_player.shooting
                player = {
                    "id": fotmob_player.id,
                    "name": name,
                    "names": {name} | fbref_player.names,
                    "country": fotmob_player.country,
                    "position": fotmob_player.position,
                    "date_of_birth": transfermarkt_player.date_of_birth,
                    "market_values": transfermarkt_player.market_values,
                    "shooting": shooting.model_dump(),
                }
                yield player
            except TypeError:
                pass

    @property
    def players(self) -> list[dict[str, typing.Any]]:
        return list(self.get_players())

    def get_players_params(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_player in self._fotmob.players:
            try:
                fbref_player = self._find_player(
                    fotmob_player,
                    self._fbref.players,
                )
                transfermarkt_player = self._find_player(
                    fotmob_player,
                    self._transfermarkt.players,
                )
                player_params = {
                    "fotmob_id": fotmob_player.id,
                    "fbref_id": fbref_player.id,
                    "fbref_path_name": fbref_player.path_name,
                    "transfermarkt_id": transfermarkt_player.id,
                    "transfermarkt_path_name": transfermarkt_player.path_name,
                }
                yield player_params
            except TypeError:
                pass

    def get_staffs_params(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for transfermarkt_staff in self._transfermarkt_staffs:
            yield {
                "transfermarkt_id": transfermarkt_staff.id,
                "transfermarkt_path_name": transfermarkt_staff.path_name,
            }


class Player:
    def __init__(
        self,
        fotmob: spiders.fotmob.player.Item,
        fbref: spiders.fbref.player.Item,
        transfermarkt: spiders.transfermarkt.player.Item,
    ) -> None:
        self._fotmob = fotmob
        self._fbref = fbref
        self._transfermarkt = transfermarkt


class Staff:
    def __init__(self, transfermarkt: spiders.transfermarkt.staff.Item) -> None:
        self._transfermarkt = transfermarkt


class Matches:
    def __init__(
        self,
        fotmob: list[spiders.fotmob.matches.Item],
    ) -> None:
        self._fotmob = fotmob

    def _find_match(
        self,
        query: BaseItem,
        choices: typing.Sequence[T],
    ) -> T:
        match = process.extractOne(
            query,
            choices,
            processor=lambda x: x.name,
        )[0]
        return match

    @property
    def info(self) -> dict[str, typing.Any]:
        return {"count": len(self.items)}

    def get_items(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_match in self._fotmob:
            yield fotmob_match.model_dump()

    @property
    def items(self) -> list[dict[str, typing.Any]]:
        return list(self.get_items())

    def get_params(
        self,
    ) -> typing.Generator[dict[str, typing.Any], typing.Any, None]:
        for fotmob_match in self._fotmob:
            match_params = {
                "fotmob_id": fotmob_match.id,
            }
            yield match_params


class Match:
    def __init__(
        self,
        fotmob: spiders.fotmob.match.Item,
    ) -> None:
        self._fotmob = fotmob
