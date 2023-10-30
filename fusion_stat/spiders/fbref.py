import httpx
from rapidfuzz import process
from parsel import Selector

from fusion_stat.base import Spider
from fusion_stat.models import (
    Stat,
    FBrefShooting,
    CompetitionFBref,
    CompetitionFBrefTeam,
    TeamFBref,
    TeamFBrefMember,
    MemberFBref,
)
from fusion_stat.utils import get_element_text, parse_fbref_shooting
from fusion_stat.config import (
    COMPETITIONS,
    COMPETITIONS_SIMILARITY_SCORE,
    COMPETITIONS_INDEX,
)


BASE_URL = "https://fbref.com/en"


class Competitions(Spider):
    module_name = "fbref"

    def parse(self, response: httpx.Response) -> tuple[Stat, ...]:
        competitions: list[Stat] = []

        selector = Selector(response.text)
        index = set()
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            id = href_strs[3]
            if id not in index:
                index.add(id)
                gender = get_element_text(
                    tr.xpath("./td[@data-stat='gender']/text()")
                )
                name = " ".join(href_strs[-1].split("-")[:-1])
                if (
                    process.extractOne(
                        name,
                        COMPETITIONS,
                        score_cutoff=COMPETITIONS_SIMILARITY_SCORE,
                    )
                    and gender == "M"
                ):
                    competitions.append(
                        Stat(
                            id=id,
                            name=name,
                        )
                    )
        return tuple(competitions)

    async def download(self) -> tuple[Stat, ...]:
        url = BASE_URL + "/comps/"
        response = await self.get(url)
        return self.parse(response)


class Competition(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: str | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name
        self.season = season

    module_name = "fbref"

    def parse(self, response: httpx.Response) -> CompetitionFBref:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/text()"))
        competition_name = " ".join(h1.split(" ")[1:-1])

        teams = []
        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            name = " ".join(href_strs[-1].split("-")[:-1])
            name_2 = get_element_text(tr.xpath("./th/a/text()"))
            shooting = parse_fbref_shooting(tr)
            teams.append(
                CompetitionFBrefTeam(
                    id=href_strs[3],
                    name=name_2,
                    path_name=name.replace(" ", "-"),
                    names={name, name_2},
                    shooting=shooting,
                )
            )
        return CompetitionFBref(
            id=self.id,
            name=competition_name,
            teams=tuple(teams),
        )

    async def download(self) -> CompetitionFBref:
        if self.season:
            path = "/comps" + f"/{self.id}/{self.season}"
            if self.path_name:
                path += f"/{self.season}-{self.path_name}-Stats"
        else:
            path = "/comps" + f"/{self.id}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"

        url = BASE_URL + path

        response = await self.get(url)
        return self.parse(response)


class Team(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: str | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name
        self.season = season

    module_name = "fbref"

    def parse(self, response: httpx.Response) -> TeamFBref:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])

        standard_stats_table = selector.xpath(
            '//table[starts-with(@id,"stats_standard_")]'
        )
        shooting_table = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]'
        )
        team_shooting = parse_fbref_shooting(
            shooting_table.xpath("./tfoot/tr[1]")
        )

        players_shooting: dict[str, FBrefShooting] = {}
        for tr in shooting_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            id = href.split("/")[3]
            shooting = parse_fbref_shooting(tr)
            players_shooting[id] = shooting

        players = []
        for tr in standard_stats_table.xpath("./tbody/tr"):
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            path_name = href_strs[-1]
            id = href_strs[3]
            name = get_element_text(tr.xpath("./th/a/text()"))
            country_code = get_element_text(
                tr.xpath('./td[@data-stat="nationality"]/a/@href')
            ).split("/")[3]

            position = get_element_text(
                tr.xpath('./td[@data-stat="position"]/text()')
            )

            try:
                shooting = players_shooting[id]
            except KeyError:
                shooting = FBrefShooting()
            players.append(
                TeamFBrefMember(
                    id=id,
                    name=name,
                    names={name, " ".join(path_name.split("-"))},
                    path_name=path_name,
                    country_code=country_code,
                    position=position,
                    shooting=shooting,
                )
            )

        return TeamFBref(
            id=self.id,
            name=team_name,
            names={team_name},
            shooting=team_shooting,
            members=tuple(players),
        )

    async def download(self) -> TeamFBref:
        if self.season:
            path = "/squads" + f"/{self.id}/{self.season}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"
        else:
            path = "/squads" + f"/{self.id}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"

        url = BASE_URL + path

        response = await self.get(url)
        return self.parse(response)


class Member(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name

    module_name = "fbref"

    def parse(self, response: httpx.Response) -> MemberFBref:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/span/text()"))

        tr = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]/tfoot/tr[1]'
        )
        shooting = parse_fbref_shooting(tr)

        return MemberFBref(id=self.id, name=name, shooting=shooting)

    async def download(self) -> MemberFBref:
        path = f"/players/{self.id}/"
        if self.path_name:
            path += self.path_name

        url = BASE_URL + path

        response = await self.get(url)
        return self.parse(response)


class Matches(Spider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.date = date

    module_name = "fbref"

    def parse(self, response: httpx.Response) -> tuple[Stat, ...]:
        selector = Selector(response.text)
        matches = []

        competitions_id_str = "|".join(
            (c.fbref_id for c in COMPETITIONS_INDEX)
        )
        tables = selector.xpath(
            f"//table[re:test(@id, 'sched_.*_({competitions_id_str})\\b')]"
        )
        trs = tables.xpath("./tbody/tr")
        # 如果还没有进行的比赛会找不到对应节点
        for tr in trs:
            try:
                home_name = get_element_text(
                    tr.xpath('./td[@data-stat="home_team"]/a/text()')
                )
                away_name = get_element_text(
                    tr.xpath('./td[@data-stat="away_team"]/a/text()')
                )

                href = get_element_text(
                    tr.xpath('./td[@data-stat="score"]/a/@href')
                )
                id = href.split("/")[3]
                matches.append(
                    Stat(
                        id=id,
                        name=f"{home_name} vs {away_name}",
                    )
                )
            except ValueError:
                pass
        return tuple(matches)

    async def download(self) -> tuple[Stat, ...]:
        path = f"/matches/{self.date}"
        url = BASE_URL + path

        response = await self.get(url)
        return self.parse(response)


class Match(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    module_name = "fbref"

    def parse(self, response: httpx.Response) -> Stat:
        selector = Selector(response.text)
        home_name, away_name = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return Stat(
            id=self.id,
            name=f"{home_name} vs {away_name}",
        )

    async def download(self) -> Stat:
        path = f"/matches/{self.id}"
        url = BASE_URL + path

        response = await self.get(url)
        return self.parse(response)
