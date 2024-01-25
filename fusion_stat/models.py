import typing

from rapidfuzz import process

from .config import COMPETITIONS, MEMBERS_SIMILARITY_SCORE
from .types import (
    base_types,
    competition_types,
    competitions_types,
    matches_types,
    member_types,
    team_types,
)
from .utils import fuzzy_similarity_mean

T = typing.TypeVar("T", bound=base_types.StatDict)
U = typing.TypeVar("U", bound=team_types.BasePlayerDict)


class Competitions:
    def __init__(
        self,
        fotmob: list[base_types.StatDict],
        fbref: list[competitions_types.FBrefCompetitionDict],
        transfermarkt: list[competitions_types.TransfermarktCompetitionDict],
        season: int | None = None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.transfermarkt = transfermarkt
        self.season = season

    def _find_competition(
        self,
        query_id: str,
        choices: typing.Sequence[T],
    ) -> T:
        for competition in choices:
            if competition["id"] == query_id:
                return competition
        raise ValueError(f"Competition with id {query_id} not found")

    @property
    def info(self) -> competitions_types.InfoDict:
        """
        Return a dict that includes the following keys:

        * count (int): number of competitions
        * names (list[str]): names of competitions
        """
        return competitions_types.InfoDict(
            count=len(COMPETITIONS),
            names=list(COMPETITIONS.keys()),
        )

    def get_items(
        self,
    ) -> typing.Generator[competitions_types.CompetitionDict, typing.Any, None]:
        """
        Return a generator of dicts that include the following keys:

        * id (str): competition id
        * name (str): config competition name
        * fotmob (dict): fotmob competition
                * id (str): fotmob competition id
                * name (str): fotmob competition name
        * fbref (dict): fbref competition
                * id (str): fbref competition id
                * name (str): fbref competition name
                * country_code (str): country code, three-letter code
        * transfermarkt (dict): transfermarkt competition
                * id (str): transfermarkt competition id
                * name (str): transfermarkt competition name
                * path_name (str): transfermarkt competition path name
        """
        for name, params in COMPETITIONS.items():
            fotmob_competition = self._find_competition(
                params["fotmob_id"], self.fotmob
            )
            fbref_competition = self._find_competition(
                params["fbref_id"], self.fbref
            )
            transfermarkt_competition = self._find_competition(
                params["transfermarkt_id"], self.transfermarkt
            )

            item = competitions_types.CompetitionDict(
                id=fotmob_competition["id"],
                name=name,
                fotmob=fotmob_competition,
                fbref=fbref_competition,
                transfermarkt=transfermarkt_competition,
            )
            yield item

    @property
    def items(self) -> list[competitions_types.CompetitionDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): competition id
        * name (str): config competition name
        * fotmob (dict): fotmob competition
                * id (str): fotmob competition id
                * name (str): fotmob competition name
        * fbref (dict): fbref competition
                * id (str): fbref competition id
                * name (str): fbref competition name
                * country_code (str): country code, three-letter code
        * transfermarkt (dict): transfermarkt competition
                * id (str): transfermarkt competition id
                * name (str): transfermarkt competition name
                * path_name (str): transfermarkt competition path name
        """
        return list(self.get_items())

    def get_params(
        self,
    ) -> typing.Generator[
        competitions_types.CompetitionParamsDict, typing.Any, None
    ]:
        """
        Return a generator of dicts that include the following keys:

            * fotmob_id (str): fotmob competition id
            * fbref_id (str): fbref competition id
            * fbref_path_name (str): fbref competition path name
            * official_name (str): config competition name
            * transfermarkt_id (str): transfermarkt competition id
            * transfermarkt_path_name (str): transfermarkt competition path name
            * season (int, optional): fotmob competition season
        """
        for item in self.get_items():
            competition_params = competitions_types.CompetitionParamsDict(
                fotmob_id=item["fotmob"]["id"],
                fbref_id=item["fbref"]["id"],
                fbref_path_name=item["fbref"]["path_name"],
                official_name=item["name"],
                transfermarkt_id=item["transfermarkt"]["id"],
                transfermarkt_path_name=item["transfermarkt"]["path_name"],
            )

            if self.season is not None:
                competition_params["season"] = self.season

            yield competition_params


class Competition:
    def __init__(
        self,
        fotmob: competition_types.FotMobDict,
        fbref: competition_types.FBrefDict,
        official: competition_types.OfficialDict,
        transfermarkt: competition_types.TransfermarktDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.official = official
        self.transfermarkt = transfermarkt

    def _find_team(
        self,
        query: base_types.StatDict,
        choices: typing.Sequence[T],
    ) -> T:
        team = process.extractOne(
            query,
            choices,
            processor=lambda x: x["name"],
        )[0]
        return team

    @property
    def info(self) -> competition_types.InfoDict:
        """
        Return a dict that includes the following keys:

        * id (str): competition id.
        * name (str): competition name.
        * logo (str): Competition logo.
        * type (str): Competition type.
        * season (str): Competition season.
        * country_code (str): country code, three-letter code
        * names (set[str]): All competition names.
        * market_values (str): Competition market values.
        * player_average_market_value (str): Competition player average market value.
        """
        return competition_types.InfoDict(
            id=self.fotmob["id"],
            name=self.fotmob["name"],
            logo=self.official["logo"],
            type=self.fotmob["type"],
            season=self.fotmob["season"],
            country_code=self.fotmob["country_code"],
            names=self.fotmob["names"] | {self.fbref["name"]},
            market_values=self.transfermarkt["market_values"],
            player_average_market_value=self.transfermarkt[
                "player_average_market_value"
            ],
        )

    def get_teams(
        self,
    ) -> typing.Generator[competition_types.TeamDict, typing.Any, None]:
        """
        Return a generator of dicts that include the following keys:

        * id (str): team id.
        * name (str): team name.
        * names (set[str]): All team names.
        * played (int): number of matches played.
        * wins (int): number of matches won.
        * draws (int): number of matches drawn.
        * losses (int): number of matches lost.
        * goals_for (int): number of goals scored.
        * goals_against (int): number of goals conceded.
        * points (int): number of points.
        * logo (str): team logo.
        * country_code (str): country code, three-letter code
        * market_values (str): team market values.
        * shooting (dict): shooting data.
                * shots (int): number of shots.
                * xg (float): expected goals.
        """
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = self._find_team(fotmob_team, self.fbref["teams"])
            official_team = self._find_team(fotmob_team, self.official["teams"])
            transfermarkt_team = self._find_team(
                fotmob_team, self.transfermarkt["teams"]
            )

            team = competition_types.TeamDict(
                **fotmob_team,
                country_code=official_team["country_code"],
                market_values=transfermarkt_team["market_values"],
                logo=official_team["logo"],
                shooting=fbref_team["shooting"],
            )
            team["names"] |= fbref_team["names"]

            yield team

    @property
    def teams(self) -> list[competition_types.TeamDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): team id.
        * name (str): team name.
        * names (set[str]): All team names.
        * played (int): number of matches played.
        * wins (int): number of matches won.
        * draws (int): number of matches drawn.
        * losses (int): number of matches lost.
        * goals_for (int): number of goals scored.
        * goals_against (int): number of goals conceded.
        * points (int): number of points.
        * logo (str): team logo.
        * country_code (str): country code, three-letter code
        * market_values (str): team market values.
        * shooting (dict): shooting data.
                * shots (int): number of shots.
                * xg (float): expected goals.
        """
        return list(self.get_teams())

    @staticmethod
    def sort_table_key(
        team: competition_types.TableTeamDict,
    ) -> tuple[int, int, int, str]:
        """
        1. 首先按照积分降序排序，积分高的排在前面
        2. 如果两个或多个球队的积分相同，则根据以下规则进行排序：
            1. 净胜球降序排序
            2. 如果净胜球也相同，则根据进球数降序排序
            3. 如果进球数也相同，则根据球队的名称（字母顺序）升序排序
        """
        goal_difference = team["goals_for"] - team["goals_against"]
        return (
            -team["points"],
            -goal_difference,
            -team["goals_for"],
            team["name"],
        )

    @property
    def table(self) -> list[competition_types.TableTeamDict]:
        """
        Return a list of dicts sorted by the standings that include the following keys:

        * id (str): team id.
        * name (str): team name.
        * played (int): number of matches played.
        * wins (int): number of matches won.
        * draws (int): number of matches drawn.
        * losses (int): number of matches lost.
        * goals_for (int): number of goals scored.
        * goals_against (int): number of goals conceded.
        * points (int): number of points.
        * xg (float): expected goals.
        * logo (str): team logo.
        """
        teams = [
            competition_types.TableTeamDict(
                id=team["id"],
                name=team["name"],
                played=team["played"],
                wins=team["wins"],
                draws=team["draws"],
                losses=team["losses"],
                goals_for=team["goals_for"],
                goals_against=team["goals_against"],
                points=team["points"],
                xg=team["shooting"]["xg"],
                logo=team["logo"],
            )
            for team in self.get_teams()
        ]
        table = sorted(teams, key=self.sort_table_key)
        return table

    def get_matches(
        self,
    ) -> typing.Generator[competition_types.MatchDict, typing.Any, None]:
        """
        Return a generator of dicts that include the following keys:

        * id (str): match id.
        * name (str): match name.
        * utc_time (str): match kickoff time.
        * finished (bool): whether the match is finished or not.
        * started (bool): whether the match has started or not.
        * cancelled (bool): whether the match is cancelled or not.
        * competition (dict): competition data.
                * id (str): competition id.
                * name (str): competition name.
        * home (dict): home team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        * away (dict): away team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        """
        for fotmob_match in self.fotmob["matches"]:
            home = fotmob_match["home"]
            away = fotmob_match["away"]
            competition = fotmob_match["competition"]
            competition["id"] = self.info["id"]

            match = competition_types.MatchDict(
                id=fotmob_match["id"],
                name=fotmob_match["name"],
                utc_time=fotmob_match["utc_time"],
                finished=fotmob_match["finished"],
                started=fotmob_match["started"],
                cancelled=fotmob_match["cancelled"],
                competition=competition,
                home=home,
                away=away,
            )
            yield match

    @property
    def matches(self) -> list[competition_types.MatchDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): match id.
        * name (str): match name.
        * utc_time (str): match kickoff time.
        * finished (bool): whether the match is finished or not.
        * started (bool): whether the match has started or not.
        * cancelled (bool): whether the match is cancelled or not.
        * competition (dict): competition data.
                * id (str): competition id.
                * name (str): competition name.
        * home (dict): home team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        * away (dict): away team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        """
        return list(self.get_matches())

    def get_teams_params(
        self,
    ) -> typing.Generator[competition_types.TeamParamsDict, typing.Any, None]:
        """
        Return a generator of dicts that include the following keys:

            * fotmob_id (str): fotmob team id
            * fbref_id (str): fbref team id
            * fbref_path_name (str): fbref team path name
            * transfermarkt_id (str): transfermarkt team id
            * transfermarkt_path_name (str): transfermarkt team path name
        """
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = self._find_team(
                fotmob_team,
                self.fbref["teams"],
            )
            transfermarkt_team = self._find_team(
                fotmob_team,
                self.transfermarkt["teams"],
            )

            team_params = competition_types.TeamParamsDict(
                fotmob_id=fotmob_team["id"],
                fbref_id=fbref_team["id"],
                fbref_path_name=fbref_team["path_name"],
                transfermarkt_id=transfermarkt_team["id"],
                transfermarkt_path_name=transfermarkt_team["path_name"],
            )
            yield team_params


class Team:
    def __init__(
        self,
        fotmob: team_types.FotMobDict,
        fbref: team_types.FBrefDict,
        transfermarkt: team_types.TransfermarktDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.transfermarkt = transfermarkt

    def _find_player(
        self,
        query: team_types.BasePlayerDict,
        choices: typing.Sequence[U],
    ) -> U:
        result = process.extractOne(
            query,
            choices,
            scorer=fuzzy_similarity_mean,
            processor=lambda x: [
                x["name"],
                x["country_code"],
                x["position"],
            ],
            score_cutoff=MEMBERS_SIMILARITY_SCORE,
        )[0]
        return result

    @property
    def info(self) -> team_types.InfoDict:
        return {
            "id": self.fotmob["id"],
            "name": self.fotmob["name"],
            "names": self.fotmob["names"] | self.fbref["names"],
            "country_code": self.fotmob["country_code"],
            "market_values": self.transfermarkt["market_values"],
        }

    @property
    def staff(self) -> team_types.StaffDict:
        return self.fotmob["staff"]

    def get_players(
        self,
    ) -> typing.Generator[team_types.PlayerDict, typing.Any, None]:
        for fotmob_player in self.fotmob["players"]:
            try:
                fbref_player = self._find_player(
                    fotmob_player,
                    self.fbref["players"],
                )
                transfermarkt_player = self._find_player(
                    fotmob_player,
                    self.transfermarkt["players"],
                )

                name = fotmob_player["name"]
                shooting = fbref_player["shooting"]
                player = team_types.PlayerDict(
                    id=fotmob_player["id"],
                    name=name,
                    names={name} | fbref_player["names"],
                    country=fotmob_player["country"],
                    position=fotmob_player["position"],
                    date_of_birth=transfermarkt_player["date_of_birth"],
                    market_values=transfermarkt_player["market_values"],
                    shooting=shooting,
                )
                yield player
            except TypeError:
                pass

    @property
    def players(self) -> list[team_types.PlayerDict]:
        return list(self.get_players())

    def get_players_params(
        self,
    ) -> typing.Generator[team_types.PlayerParamsDict, typing.Any, None]:
        for fotmob_player in self.fotmob["players"]:
            try:
                fbref_player = self._find_player(
                    fotmob_player,
                    self.fbref["players"],
                )
                transfermarkt_player = self._find_player(
                    fotmob_player,
                    self.transfermarkt["players"],
                )
                player_params = team_types.PlayerParamsDict(
                    fotmob_id=fotmob_player["id"],
                    fbref_id=fbref_player["id"],
                    fbref_path_name=fbref_player["path_name"],
                    transfermarkt_id=transfermarkt_player["id"],
                    transfermarkt_path_name=transfermarkt_player["path_name"],
                )
                yield player_params
            except TypeError:
                pass


class Member:
    def __init__(
        self,
        fotmob: member_types.FotMobDict,
        fbref: member_types.FBrefDict,
        transfermarkt: member_types.TransfermarktDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.transfermarkt = transfermarkt


class Matches:
    def __init__(
        self,
        fotmob: list[matches_types.FotMobMatchDict],
        fbref: list[base_types.StatDict],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    def _find_match(
        self,
        query: base_types.StatDict,
        choices: typing.Sequence[T],
    ) -> T:
        match = process.extractOne(
            query,
            choices,
            processor=lambda x: x["name"],
        )[0]
        return match

    def get_items(
        self,
    ) -> typing.Generator[matches_types.MatchDict, typing.Any, None]:
        """
        Return a generator of dicts that include the following keys:

        * id (str): match id.
        * name (str): match name.
        * utc_time (str): match kickoff time.
        * finished (bool): whether the match is finished or not.
        * started (bool): whether the match has started or not.
        * cancelled (bool): whether the match is cancelled or not.
        * competition (dict): competition data.
                * id (str): competition id.
                * name (str): competition name.
        * home (dict): home team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        * away (dict): away team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        """
        for fotmob_match in self.fotmob:
            match = matches_types.MatchDict(**fotmob_match)
            yield match

    @property
    def items(self) -> list[matches_types.MatchDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): match id.
        * name (str): match name.
        * utc_time (str): match kickoff time.
        * finished (bool): whether the match is finished or not.
        * started (bool): whether the match has started or not.
        * cancelled (bool): whether the match is cancelled or not.
        * competition (dict): competition data.
                * id (str): competition id.
                * name (str): competition name.
        * home (dict): home team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        * away (dict): away team data.
                * id (str): team id.
                * name (str): team name.
                * score (int | None): match score.
        """
        return list(self.get_items())

    @property
    def info(self) -> matches_types.InfoDict:
        return matches_types.InfoDict(count=len(self.items))

    def get_params(
        self,
    ) -> typing.Generator[matches_types.MatchParamsDict, typing.Any, None]:
        for fotmob_match in self.fotmob:
            if not fotmob_match["cancelled"]:
                fbref_match = self._find_match(fotmob_match, self.fbref)

                match_params = matches_types.MatchParamsDict(
                    fotmob_id=fotmob_match["id"], fbref_id=fbref_match["id"]
                )
                yield match_params


class Match:
    def __init__(
        self,
        fotmob: base_types.StatDict,
        fbref: base_types.StatDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
