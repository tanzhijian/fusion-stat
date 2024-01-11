import httpx
from parsel import Selector, SelectorList

from ..base import Spider
from ..config import COMPETITIONS
from ..types import (
    base_types,
    competition_types,
    competitions_types,
    member_types,
    team_types,
)
from ..utils import get_element_text

BASE_URL = "https://fbref.com/en"


class Competitions(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", url=BASE_URL + "/comps/")

    def parse(
        self, response: httpx.Response
    ) -> list[competitions_types.FBrefCompetitionDict]:
        competitions: list[competitions_types.FBrefCompetitionDict] = []

        selector = Selector(response.text)
        competitions_id = {
            params["fbref_id"] for params in COMPETITIONS.values()
        }
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            id = href_strs[3]
            if id in competitions_id:
                # 在没有国家代码的赛事统一采用 fotmob 的规则，命名为 INT
                country_code = (
                    tr.xpath('./td[@data-stat="country"]/a[2]/text()').get()
                    or "INT"
                )
                name = " ".join(href_strs[-1].split("-")[:-1])
                competitions.append(
                    competitions_types.FBrefCompetitionDict(
                        id=id,
                        name=name,
                        country_code=country_code,
                    )
                )
        return competitions


class Competition(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name
        if season is None:
            self.season = season
        else:
            self.season = f"{season}-{season + 1}"

    @property
    def request(self) -> httpx.Request:
        if self.season:
            path = "/comps" + f"/{self.id}/{self.season}"
            if self.path_name:
                path += f"/{self.season}-{self.path_name}-Stats"
        else:
            path = "/comps" + f"/{self.id}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"

        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> competition_types.FBrefDict:
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
            shooting = parse_shooting(tr)
            teams.append(
                competition_types.FBrefTeamDict(
                    id=href_strs[3],
                    name=name_2,
                    path_name=name.replace(" ", "-"),
                    names={name, name_2},
                    shooting=shooting,
                )
            )
        return competition_types.FBrefDict(
            id=self.id,
            name=competition_name,
            teams=teams,
        )


class Team(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: int | None = None,
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__(client=client)
        self.id = id
        self.path_name = path_name
        if season is None:
            self.season = season
        else:
            self.season = f"{season}-{season + 1}"

    @property
    def request(self) -> httpx.Request:
        if self.season:
            path = "/squads" + f"/{self.id}/{self.season}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"
        else:
            path = "/squads" + f"/{self.id}"
            if self.path_name:
                path += f"/{self.path_name}-Stats"

        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> team_types.FBrefDict:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/span/text()"))
        team_name = " ".join(h1.split(" ")[1:-1])

        standard_stats_table = selector.xpath(
            '//table[starts-with(@id,"stats_standard_")]'
        )
        shooting_table = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]'
        )
        team_shooting = parse_shooting(shooting_table.xpath("./tfoot/tr[1]"))

        players_shooting: dict[str, base_types.FBrefShootingDict] = {}
        for tr in shooting_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            id = href.split("/")[3]
            shooting = parse_shooting(tr)
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
                shooting = base_types.FBrefShootingDict(shots=0, xg=0)
            players.append(
                team_types.FBrefMemberDict(
                    id=id,
                    name=name,
                    names={name, " ".join(path_name.split("-"))},
                    path_name=path_name,
                    country_code=country_code,
                    position=position,
                    shooting=shooting,
                )
            )

        return team_types.FBrefDict(
            id=self.id,
            name=team_name,
            names={team_name},
            shooting=team_shooting,
            members=players,
        )


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

    @property
    def request(self) -> httpx.Request:
        path = f"/players/{self.id}/"
        if self.path_name:
            path += self.path_name

        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> member_types.FBrefDict:
        selector = Selector(response.text)
        name = get_element_text(selector.xpath("//h1/span/text()"))

        tr = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]/tfoot/tr[1]'
        )
        shooting = parse_shooting(tr)

        return member_types.FBrefDict(id=self.id, name=name, shooting=shooting)


class Matches(Spider):
    """Parameters:

    * date: "%Y-%m-%d", such as "2023-09-03"
    """

    def __init__(self, *, date: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.date = date

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.date}"
        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> list[base_types.StatDict]:
        selector = Selector(response.text)
        matches = []

        competitions_id_str = "|".join(
            (c["fbref_id"] for c in COMPETITIONS.values())
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
                    base_types.StatDict(
                        id=id,
                        name=f"{home_name} vs {away_name}",
                    )
                )
            except ValueError:
                pass
        return matches


class Match(Spider):
    def __init__(self, *, id: str, client: httpx.AsyncClient) -> None:
        super().__init__(client=client)
        self.id = id

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.id}"
        return httpx.Request("GET", url=BASE_URL + path)

    def parse(self, response: httpx.Response) -> base_types.StatDict:
        selector = Selector(response.text)
        home_name, away_name = selector.xpath(
            '//div[@class="scorebox"]//strong/a/text()'
        ).getall()[:2]
        return base_types.StatDict(
            id=self.id,
            name=f"{home_name} vs {away_name}",
        )


def parse_shooting(
    tr: Selector | SelectorList[Selector],
) -> base_types.FBrefShootingDict:
    shots = get_element_text(tr.xpath('./td[@data-stat="shots"]/text()'))
    xg = get_element_text(tr.xpath('./td[@data-stat="xg"]/text()'))
    return base_types.FBrefShootingDict(
        shots=int(shots),
        xg=float(xg),
    )
