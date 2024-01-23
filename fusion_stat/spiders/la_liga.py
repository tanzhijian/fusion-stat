import httpx

from ..scraper import Spider
from ..types import competition_types
from ..utils import current_season

HEADERS = {
    "Ocp-Apim-Subscription-Key": "c13c3a8e2f6b46da9c5c425cf61fab3e",
}


class Competition(Spider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
        self.name = name
        if season:
            self.season = season
        else:
            self.season = current_season()[0]

        if self.season == 2023:
            self.slug = f"laliga-easports-{self.season}"
        else:
            self.slug = f"laliga-santander-{self.season}"

    @property
    def request(self) -> httpx.Request:
        url = (
            "https://apim.laliga.com/public-service/api/v1"
            f"/teams?subscriptionSlug={self.slug}"
            "&limit=99&offset=0&orderField=nickname&orderType=ASC"
        )
        return httpx.Request("GET", url=url, headers=HEADERS)

    def parse(self, response: httpx.Response) -> competition_types.OfficialDict:
        json = response.json()
        teams = []
        for team in json["teams"]:
            teams.append(
                competition_types.OfficialTeamDict(
                    id=team["slug"],
                    name=team["nickname"],
                    country_code="ESP",
                    logo=team["shield"]["resizes"]["small"],
                )
            )
        return competition_types.OfficialDict(
            id=self.slug,
            name=self.name,
            logo=(
                "https://cdn.cookielaw.org/logos"
                "/f99d5762-5a8e-4e1e-b9e9-e5c54ec8ea01"
                "/ad294791-9034-442d-ab46-e1d94e100d71"
                "/629b7af6-84a6-4437-ae29-fefaefb3f5d2"
                "/RGB_Logotipo_LALIGA_coral.png"
            ),
            teams=teams,
        )
