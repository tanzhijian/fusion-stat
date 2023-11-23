import httpx

from fusion_stat.base import Spider
from fusion_stat.models import (
    CompetitionOfficial,
    CompetitionOfficialTeam,
)
from fusion_stat.utils import current_season


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
        # 余 100 获取赛季最后两位数字
        if season:
            self.season = f"{season}-{(season + 1) % 100}"
        else:
            _current_season = current_season()
            self.season = f"{_current_season[0]}-{_current_season[1] % 100}"

    @property
    def request(self) -> httpx.Request:
        url = (
            "https://www.legaseriea.it/api/stats/Classificacompleta?"
            f"CAMPIONATO=A&STAGIONE={self.season}&TURNO=UNICO&GIRONE=UNI"
        )
        return httpx.Request("GET", url=url)

    def parse(self, response: httpx.Response) -> CompetitionOfficial:
        json = response.json()
        teams = []
        for team in json["data"]:
            teams.append(
                CompetitionOfficialTeam(
                    id=team["team_slug"].split("/")[-1],
                    name=team["Nome"].title(),
                    logo=team["team_image"],
                )
            )
        return CompetitionOfficial(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                "https://img.legaseriea.it/vimages"
                "/62cef685/SerieA_RGB.jpg?webp&q=70&size=-x0"
            ),
            teams=tuple(teams),
        )
