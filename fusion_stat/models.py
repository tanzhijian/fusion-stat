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
from .utils import concatenate_strings, fuzzy_similarity_mean

T = typing.TypeVar("T", bound=base_types.StatDict)


class Competitions:
    def __init__(
        self,
        fotmob: list[base_types.StatDict],
        fbref: list[competitions_types.FBrefCompetitionDict],
        season: int | None = None,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.season = season

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

    @property
    def items(self) -> list[competitions_types.CompetitionDict]:
        """
        Return a list of dicts that include the following keys:

        * id (str): fotmob competition id
        * name (str): config competition name
        * fotmob (dict): fotmob competition
                * id (str): fotmob competition id
                * name (str): fotmob competition name
        * fbref (dict): fbref competition
                * id (str): fbref competition id
                * name (str): fbref competition name
        """
        items: list[competitions_types.CompetitionDict] = []
        for name, params in COMPETITIONS.items():
            fotmob_competition = self._find_competition_by_id(
                self.fotmob, params["fotmob_id"]
            )
            fbref_competition = self._find_competition_by_id(
                self.fbref, params["fbref_id"]
            )

            name = fotmob_competition["name"]
            code = (
                fbref_competition["country_code"]
                or fbref_competition["governing_body"]
                or ""
            )
            id = concatenate_strings(code, name)

            item = competitions_types.CompetitionDict(
                id=id,
                name=name,
                fotmob=fotmob_competition,
                fbref=fbref_competition,
            )
            items.append(item)
        return items

    def _find_competition_by_id(
        self, competitions: list[T], competition_id: str
    ) -> T:
        for competition in competitions:
            if competition["id"] == competition_id:
                return competition
        raise ValueError(f"Competition with id {competition_id} not found")

    def get_params(self) -> list[competitions_types.CompetitionParamsDict]:
        """
        Return a list of dicts that include the following keys:

            * fotmob_id (str): fotmob competition id
            * fbref_id (str): fbref competition id
            * fbref_path_name (str): fbref competition path name
            * official_name (str): config competition name
            * season (int, optional): fotmob competition season
        """
        params: list[competitions_types.CompetitionParamsDict] = []

        for item in self.items:
            competition_params = competitions_types.CompetitionParamsDict(
                fotmob_id=item["fotmob"]["id"],
                fbref_id=item["fbref"]["id"],
                fbref_path_name=item["fbref"]["name"].replace(" ", "-"),
                official_name=item["name"],
            )

            if self.season is not None:
                competition_params["season"] = self.season

            params.append(competition_params)

        return params


class Competition:
    def __init__(
        self,
        fotmob: competition_types.FotMobDict,
        fbref: competition_types.FBrefDict,
        official: competition_types.OfficialDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
        self.official = official

    @property
    def info(self) -> competition_types.InfoDict:
        """
        Return a dict that includes the following keys:

        * id (str): competition id.
        * name (str): competition name.
        * logo (str): Competition logo.
        * type (str): Competition type.
        * season (str): Competition season.
        * names (set[str]): All competition names.
        """
        return {
            "id": self.fotmob["id"],
            "name": self.fotmob["name"],
            "logo": self.official["logo"],
            "type": self.fotmob["type"],
            "season": self.fotmob["season"],
            "names": self.fotmob["names"] | {self.fbref["name"]},
        }

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
        * shooting (dict): shooting data.
                * shots (int): number of shots.
                * xg (float): expected goals.
        """
        teams: list[competition_types.TeamDict] = []
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = process.extractOne(
                fotmob_team,
                self.fbref["teams"],
                processor=lambda x: x["name"],
            )[0]
            official_team = process.extractOne(
                fotmob_team,
                self.official["teams"],
                processor=lambda x: x["name"],
            )[0]

            team = competition_types.TeamDict(
                **fotmob_team,
                logo=official_team["logo"],
                shooting=fbref_team["shooting"],
            )
            team["names"] |= fbref_team["names"]
            teams.append(team)
        return teams

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
            for team in self.teams
        ]
        table = sorted(teams, key=self.sort_table_key)
        return table

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
        return [
            competition_types.MatchDict(**match)
            for match in self.fotmob["matches"]
        ]

    def get_teams_params(self) -> list[competition_types.TeamParamsDict]:
        params: list[competition_types.TeamParamsDict] = []
        for fotmob_team in self.fotmob["teams"]:
            fbref_team = process.extractOne(
                fotmob_team,
                self.fbref["teams"],
                processor=lambda x: x["name"],
            )[0]

            team_params = competition_types.TeamParamsDict(
                fotmob_id=fotmob_team["id"],
                fbref_id=fbref_team["id"],
                fbref_path_name=fbref_team["path_name"],
            )

            params.append(team_params)
        return params


class Team:
    def __init__(
        self,
        fotmob: team_types.FotMobDict,
        fbref: team_types.FBrefDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

    @property
    def info(self) -> team_types.InfoDict:
        return {
            "id": self.fotmob["id"],
            "name": self.fotmob["name"],
            "names": self.fotmob["names"] | self.fbref["names"],
        }

    @property
    def staff(self) -> list[team_types.StaffDict]:
        return [
            {
                "id": member["id"],
                "name": member["name"],
                "country": member["country"],
            }
            for member in self.fotmob["members"]
            if member["is_staff"]
        ]

    @property
    def players(self) -> list[team_types.PlayerDict]:
        players: list[team_types.PlayerDict] = []
        for fotmob_member in self.fotmob["members"]:
            if not fotmob_member["is_staff"]:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref["members"],
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x["name"],
                            x["country_code"],
                            x["position"],
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]

                    shooting = fbref_member["shooting"]
                    players.append(
                        team_types.PlayerDict(
                            id=fotmob_member["id"],
                            name=fotmob_member["name"],
                            names={fotmob_member["name"]}
                            | fbref_member["names"],
                            country=fotmob_member["country"],
                            position=fotmob_member["position"],
                            shooting=shooting,
                        )
                    )
                except TypeError:
                    pass

        return players

    def get_members_params(self) -> list[team_types.MemberParamsDict]:
        params: list[team_types.MemberParamsDict] = []
        for fotmob_member in self.fotmob["members"]:
            if not fotmob_member["is_staff"]:
                try:
                    fbref_member = process.extractOne(
                        fotmob_member,
                        self.fbref["members"],
                        scorer=fuzzy_similarity_mean,
                        processor=lambda x: [
                            x["name"],
                            x["country_code"],
                            x["position"],
                        ],
                        score_cutoff=MEMBERS_SIMILARITY_SCORE,
                    )[0]
                    member_params = team_types.MemberParamsDict(
                        fotmob_id=fotmob_member["id"],
                        fbref_id=fbref_member["id"],
                        fbref_path_name=fbref_member["path_name"],
                    )
                    params.append(member_params)
                except TypeError:
                    pass
        return params


class Member:
    def __init__(
        self,
        fotmob: member_types.FotMobDict,
        fbref: member_types.FBrefDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Matches:
    def __init__(
        self,
        fotmob: list[matches_types.FotMobMatchDict],
        fbref: list[base_types.StatDict],
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref

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
        return [matches_types.MatchDict(**match) for match in self.fotmob]

    @property
    def info(self) -> matches_types.InfoDict:
        return matches_types.InfoDict(count=len(self.items))

    def get_params(self) -> list[matches_types.MatchParamsDict]:
        if not self.fbref:
            raise ValueError("No fbref id for the current date")
        params: list[matches_types.MatchParamsDict] = []
        for fotmob_match in self.fotmob:
            if not fotmob_match["cancelled"]:
                fbref_match = process.extractOne(
                    fotmob_match, self.fbref, processor=lambda x: x["name"]
                )[0]

                match_params = matches_types.MatchParamsDict(
                    fotmob_id=fotmob_match["id"], fbref_id=fbref_match["id"]
                )
                params.append(match_params)
        return params


class Match:
    def __init__(
        self,
        fotmob: base_types.StatDict,
        fbref: base_types.StatDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
