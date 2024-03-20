import typing

import httpx
from parsel import Selector

from ...scraper import BaseItem, BaseSpider
from ...utils import current_season, get_element_text
from ._common import PREMIER_LEAGUE_COMPETITIONS_SEASON_INDEX, BaseURL, Headers


class TeamItem(BaseItem):
    country_code: str
    logo: str


class Item(BaseItem):
    logo: str
    teams: list[TeamItem]


class Spider(BaseSpider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
        self.name = name
        self.season = season
        self.spider = spiders_cls[self.name](
            **{"name": self.name, "season": self.season}
        )

    @property
    def request(self) -> httpx.Request:
        return self.spider.request

    def parse(self, response: httpx.Response) -> typing.Any:
        return self.spider.parse(response)


class BundesligaSpider(BaseSpider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
        self.name = name
        _current_season = current_season()
        if season:
            self.is_current_season = season == _current_season[0]
            self.season = f"{season}-{season + 1}"
        else:
            self.is_current_season = True
            self.season = f"{_current_season[0]}-{_current_season[1]}"

    @property
    def request(self) -> httpx.Request:
        if self.is_current_season:
            path = "/en/bundesliga/clubs"
        else:
            path = f"/assets/historic-season/{self.season}.json"
        return httpx.Request("GET", url=f"{BaseURL.bundesliga}{path}")

    def parse(self, response: httpx.Response) -> Item:
        # competition historic api 没有当前赛季
        # 而且在 22 赛季以前使用的 id 与之后是不一样的
        if self.is_current_season:
            teams = self._parse_current_season_teams(response)
        else:
            teams = self._parse_historic_season_teams(response)
        return Item(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=f"{BaseURL.bundesliga}/assets/favicons/safari-pinned-tab_new.svg",
            teams=teams,
        )

    def _parse_current_season_teams(
        self, response: httpx.Response
    ) -> list[TeamItem]:
        selector = Selector(response.text)
        club_cards = selector.xpath('//div[@class="clubs grid"]/club-card')
        teams = []
        for card in club_cards:
            id_ = get_element_text(card.xpath("./a/@href")).split("/")[-1]

            img = card.xpath(".//img")
            name = get_element_text(img.xpath("./@alt"))
            logo_path = get_element_text(img.xpath("./@src")[0])
            logo = f"{BaseURL.bundesliga}{logo_path}"

            teams.append(
                TeamItem(
                    id=id_,
                    name=name,
                    country_code="GER",
                    logo=logo,
                )
            )
        return teams

    def _parse_historic_season_teams(
        self, response: httpx.Response
    ) -> list[TeamItem]:
        json = response.json()
        teams = []
        for team in json["entries"]:
            club = team["club"]

            id_ = club["slugifiedFull"]
            name = club["nameFull"]

            club_id = club["id"]
            if club["logoUrl"]:
                logo = f"{BaseURL.bundesliga}/assets/clublogo/{club_id}.svg"
            else:
                logo = ""

            teams.append(
                TeamItem(
                    id=id_,
                    name=name,
                    country_code="GER",
                    logo=logo,
                )
            )
        return teams


class LaLigaSpider(BaseSpider):
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
        return httpx.Request("GET", url=url, headers=Headers.la_liga)

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        teams = []
        for team in json["teams"]:
            teams.append(
                TeamItem(
                    id=team["slug"],
                    name=team["nickname"],
                    country_code="ESP",
                    logo=team["shield"]["resizes"]["small"],
                )
            )
        return Item(
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


class Ligue1Spider(BaseSpider):
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
        return httpx.Request("GET", url=f"{BaseURL.ligue_1}{path}")

    def parse(self, response: httpx.Response) -> Item:
        selector = Selector(response.text)
        club_list = selector.xpath('//div[@class="ClubListPage-list"]/a')
        teams = []
        for team in club_list:
            id_ = get_element_text(team.xpath("./@href")).split("=")[-1]

            img = team.xpath(".//img")
            logo_path = get_element_text(img.xpath("./@data-src"))
            logo = f"{BaseURL.ligue_1}{logo_path}"

            name = get_element_text(img.xpath("./@alt"))
            name = self._fix_name(name)

            teams.append(
                TeamItem(
                    id=id_,
                    name=name,
                    country_code="FRA",
                    logo=logo,
                )
            )
        return Item(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                f"{BaseURL.ligue_1}/-/media/Project/LFP/shared/Images"
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


class PremierLeagueSpider(BaseSpider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
        self.name = name
        if season:
            self.season = str(season)
        else:
            self.season = str(current_season()[0])

    @property
    def request(self) -> httpx.Request:
        path = (
            "/teams?pageSize=100"
            f"&compSeasons={PREMIER_LEAGUE_COMPETITIONS_SEASON_INDEX[self.name][self.season]}"
            "&comps=1&altIds=true&page=0"
        )
        return httpx.Request(
            "GET",
            url=f"{BaseURL.premier_league}{path}",
            headers=Headers.premier_league,
        )

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        teams = []
        for team in json["content"]:
            id_ = str(int(team["club"]["id"]))
            name = team["name"]
            image_id = team["altIds"]["opta"]
            logo = (
                "https://resources.premierleague.com/premierleague"
                f"/badges/rb/{image_id}.svg"
            )
            teams.append(
                TeamItem(
                    id=id_,
                    name=name,
                    country_code="ENG",
                    logo=logo,
                )
            )

        return Item(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                "https://www.premierleague.com/resources/rebrand"
                "/v7.129.2/i/elements/pl-main-logo.png"
            ),
            teams=teams,
        )


class SerieASpider(BaseSpider):
    def __init__(
        self,
        *,
        name: str,
        season: int | None = None,
    ) -> None:
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

    def parse(self, response: httpx.Response) -> Item:
        json = response.json()
        teams = []
        for team in json["data"]:
            teams.append(
                TeamItem(
                    id=team["team_slug"].split("/")[-1],
                    name=team["Nome"].title(),
                    country_code="ITA",
                    logo=team["team_image"],
                )
            )
        return Item(
            id=f"{self.name} {self.season}",
            name=self.name,
            logo=(
                "https://img.legaseriea.it/vimages"
                "/62cef685/SerieA_RGB.jpg?webp&q=70&size=-x0"
            ),
            teams=teams,
        )


spiders_cls: dict[str, type[BaseSpider]] = {
    "Premier League": PremierLeagueSpider,
    "La Liga": LaLigaSpider,
    "Bundesliga": BundesligaSpider,
    "Serie A": SerieASpider,
    "Ligue 1": Ligue1Spider,
}
