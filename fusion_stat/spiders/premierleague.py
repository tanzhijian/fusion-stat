import httpx

from fusion_stat.base import Spider
from fusion_stat.utils import current_season
from fusion_stat.models import (
    CompetitionPremierLeague,
    CompetitionPremierLeagueTeam,
)


BASE_URL = "https://footballapi.pulselive.com/football"
HEADERS = {
    "Origin": "https://www.premierleague.com",
}
SEASON_INDEX = {
    "2023": "578",
    "2022": "489",
}


class Competition(Spider):
    def __init__(
        self,
        *,
        season: str | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        if season:
            self.season = season
        else:
            self.season = str(current_season()[0])

    @property
    def request(self) -> httpx.Request:
        path = (
            f"/teams?pageSize=100&compSeasons={SEASON_INDEX[self.season]}"
            "&comps=1&altIds=true&page=0"
        )
        return httpx.Request(
            "GET",
            url=BASE_URL + path,
            headers=HEADERS,
        )

    def parse(self, response: httpx.Response) -> CompetitionPremierLeague:
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
            teams.append(
                CompetitionPremierLeagueTeam(id=id, name=name, logo=logo)
            )

        return CompetitionPremierLeague(
            id="Premier League",
            name="Premier League",
            logo=(
                "https://www.premierleague.com/resources/rebrand"
                "/v7.129.2/i/elements/pl-main-logo.png"
            ),
            teams=tuple(teams),
        )
