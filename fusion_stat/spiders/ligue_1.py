import httpx
from parsel import Selector

from ..scraper import Spider
from ..types import competition_types
from ..utils import current_season, get_element_text

BASE_URL = "https://www.ligue1.com"


class Competition(Spider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
        self.name = name
        if season:
            self.season = f"{season}-{season + 1}"
        else:
            _current_season = current_season()
            self.season = f"{_current_season[0]}-{_current_season[1]}"

    @property
    def request(self) -> httpx.Request:
        path = f"/clubs/List?seasonId={self.season}"
        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> competition_types.OfficialDict:
        selector = Selector(response.text)
        club_list = selector.xpath('//div[@class="ClubListPage-list"]/a')
        teams = []
        for team in club_list:
            id = get_element_text(team.xpath("./@href")).split("=")[-1]

            img = team.xpath(".//img")
            logo = BASE_URL + get_element_text(img.xpath("./@data-src"))

            name = get_element_text(img.xpath("./@alt"))
            name = self._fix_name(name)

            teams.append(
                competition_types.OfficialTeamDict(
                    id=id,
                    name=name,
                    country_code="FRA",
                    logo=logo,
                )
            )
        return competition_types.OfficialDict(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                f"{BASE_URL}/-/media/Project/LFP/shared/Images"
                "/Competition/Favicon/L1-favicon.png"
            ),
            teams=teams,
        )

    def _fix_name(self, name: str) -> str:
        """name 用于 rapidfuzz 匹配临时修正方案

        >>> fuzz.ratio("Rennes", "Stade Rennais Fc")
        45.45454545454546
        >>> fuzz.ratio("Rennes", "Rc Lens")
        61.53846153846154

        """
        if name == "STADE RENNAIS FC":
            name = "Rennes"
        return name.title()
