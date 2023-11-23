import httpx

from fusion_stat.base import Spider
from fusion_stat.models import (
    CompetitionOfficial,
    CompetitionOfficialTeam,
    CompetitionsPremierLeagueCompetition,
    Stat,
)
from fusion_stat.utils import current_season

BASE_URL = "https://footballapi.pulselive.com/football"
HEADERS = {
    "Origin": "https://www.premierleague.com",
}
COMPETITIONS_SEASON_INDEX = {
    "Premier League": {
        "2023": "578",
        "2022": "489",
        "2021": "418",
        "2020": "363",
        "2019": "274",
        "2018": "210",
        "2017": "79",
        "2016": "54",
        "2015": "42",
        "2014": "27",
        "2013": "22",
        "2012": "21",
        "2011": "20",
        "2010": "19",
        "2009": "18",
        "2008": "17",
        "2007": "16",
        "2006": "15",
        "2005": "14",
        "2004": "13",
        "2003": "12",
        "2002": "11",
        "2001": "10",
        "2000": "9",
        "1999": "8",
        "1998": "7",
        "1997": "6",
        "1996": "5",
        "1995": "4",
        "1994": "3",
        "1993": "2",
        "1992": "1",
    }
}


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request(
            "GET",
            url=(
                "https://footballapi.pulselive.com/football"
                "/competitions?page=0&pageSize=1000&detail=2"
            ),
            headers=HEADERS,
        )

    def parse(
        self, response: httpx.Response
    ) -> tuple[CompetitionsPremierLeagueCompetition, ...]:
        json = response.json()
        # only pl
        pl = json["content"][1]
        seasons = [
            Stat(
                id=str(int(season["id"])),
                name=season["label"],
            )
            for season in pl["compSeasons"]
        ]
        return (
            CompetitionsPremierLeagueCompetition(
                id=pl["description"],
                name=pl["description"],
                seasons=tuple(seasons),
            ),
        )

    def index(
        self, competitions: tuple[CompetitionsPremierLeagueCompetition, ...]
    ) -> dict[str, dict[str, str]]:
        """Generate COMPETITIONS_SEASON_INDEX"""
        competitions_seasons_index = {}
        for competition in competitions:
            seasons_index = {}
            for season in competition.seasons:
                seasons_index[season.name.split("/")[0]] = season.id
            competitions_seasons_index[competition.name] = seasons_index
        return competitions_seasons_index


class Competition(Spider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.name = name
        if season:
            self.season = str(season)
        else:
            self.season = str(current_season()[0])

    @property
    def request(self) -> httpx.Request:
        path = (
            "/teams?pageSize=100"
            f"&compSeasons={COMPETITIONS_SEASON_INDEX[self.name][self.season]}"
            "&comps=1&altIds=true&page=0"
        )
        return httpx.Request(
            "GET",
            url=BASE_URL + path,
            headers=HEADERS,
        )

    def parse(self, response: httpx.Response) -> CompetitionOfficial:
        json = response.json()
        teams = []
        for team in json["content"]:
            id = str(int(team["club"]["id"]))
            name = team["name"]
            image_id = team["altIds"]["opta"]
            logo = (
                "https://resources.premierleague.com/premierleague"
                f"/badges/rb/{image_id}.svg"
            )
            teams.append(CompetitionOfficialTeam(id=id, name=name, logo=logo))

        return CompetitionOfficial(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                "https://www.premierleague.com/resources/rebrand"
                "/v7.129.2/i/elements/pl-main-logo.png"
            ),
            teams=tuple(teams),
        )
