import httpx
from parsel import Selector, SelectorList

from ..config import COMPETITIONS
from ..scraper import Spider
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
        return httpx.Request("GET", url=f"{BASE_URL}/comps/")

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
            id_ = href_strs[3]
            if id_ in competitions_id:
                # 在没有国家代码的赛事统一采用 fotmob 的规则，命名为 INT
                country_code = (
                    tr.xpath('./td[@data-stat="country"]/a[2]/text()').get()
                    or "INT"
                )
                path_name_strs = href_strs[-1].split("-")[:-1]
                path_name = "-".join(path_name_strs)
                name = " ".join(path_name_strs)
                competitions.append(
                    competitions_types.FBrefCompetitionDict(
                        id=id_,
                        name=name,
                        path_name=path_name,
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
    ) -> None:
        self.id = id
        self.path_name = path_name
        if season is None:
            self.season = season
        else:
            self.season = f"{season}-{season + 1}"

    @property
    def request(self) -> httpx.Request:
        if self.season:
            path = f"/comps/{self.id}/{self.season}"
            if self.path_name:
                path = f"{path}/{self.season}-{self.path_name}-Stats"
        else:
            path = f"/comps/{self.id}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> competition_types.FBrefDict:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/text()"))
        name = " ".join(h1.split(" ")[1:-1])

        teams: list[competition_types.FBrefTeamDict] = []
        trs = selector.xpath(
            '//table[@id="stats_squads_shooting_for"]/tbody/tr'
        )
        for tr in trs:
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            team_path_name_strs = href_strs[-1].split("-")[:-1]
            team_path_name = "-".join(team_path_name_strs)
            team_name = " ".join(team_path_name_strs)
            team_name_2 = get_element_text(tr.xpath("./th/a/text()"))
            shooting = parse_shooting(tr)
            teams.append(
                competition_types.FBrefTeamDict(
                    id=href_strs[3],
                    name=team_name_2,
                    names={team_name, team_name_2},
                    path_name=team_path_name,
                    shooting=shooting,
                )
            )
        return competition_types.FBrefDict(
            id=self.id,
            name=name,
            teams=teams,
        )


class Team(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
        season: int | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name
        if season is None:
            self.season = season
        else:
            self.season = f"{season}-{season + 1}"

    @property
    def request(self) -> httpx.Request:
        if self.season:
            path = f"/squads/{self.id}/{self.season}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"
        else:
            path = f"/squads/{self.id}"
            if self.path_name:
                path = f"{path}/{self.path_name}-Stats"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> team_types.FBrefDict:
        selector = Selector(response.text)
        h1 = get_element_text(selector.xpath("//h1/span[1]/text()"))
        name = " ".join(h1.split(" ")[1:-1])

        standard_stats_table = selector.xpath(
            '//table[starts-with(@id,"stats_standard_")]'
        )
        shooting_table = selector.xpath(
            '//table[starts-with(@id,"stats_shooting_")]'
        )
        shooting = parse_shooting(shooting_table.xpath("./tfoot/tr[1]"))

        players_shooting_index: dict[str, base_types.FBrefShootingDict] = {}
        for tr in shooting_table.xpath("./tbody/tr"):
            href = get_element_text(tr.xpath("./th/a/@href"))
            player_id = href.split("/")[3]
            player_shooting = parse_shooting(tr)
            players_shooting_index[player_id] = player_shooting

        players: list[team_types.FBrefPlayerDict] = []
        for tr in standard_stats_table.xpath("./tbody/tr"):
            href_strs = get_element_text(tr.xpath("./th/a/@href")).split("/")
            player_path_name = href_strs[-1]
            player_id = href_strs[3]
            player_name = get_element_text(tr.xpath("./th/a/text()"))
            country_code = get_element_text(
                tr.xpath('./td[@data-stat="nationality"]/a/@href')
            ).split("/")[3]

            position = get_element_text(
                tr.xpath('./td[@data-stat="position"]/text()')
            )
            try:
                player_shooting = players_shooting_index[player_id]
            except KeyError:
                player_shooting = base_types.FBrefShootingDict(shots=0, xg=0)
            players.append(
                team_types.FBrefPlayerDict(
                    id=player_id,
                    name=player_name,
                    names={player_name, " ".join(player_path_name.split("-"))},
                    path_name=player_path_name,
                    country_code=country_code,
                    position=position,
                    shooting=player_shooting,
                )
            )

        return team_types.FBrefDict(
            id=self.id,
            name=name,
            names={name},
            shooting=shooting,
            players=players,
        )


class Member(Spider):
    def __init__(
        self,
        *,
        id: str,
        path_name: str | None = None,
    ) -> None:
        self.id = id
        self.path_name = path_name

    @property
    def request(self) -> httpx.Request:
        path = f"/players/{self.id}/"
        if self.path_name:
            path = f"{path}{self.path_name}"

        return httpx.Request("GET", url=f"{BASE_URL}{path}")

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

    def __init__(self, *, date: str) -> None:
        self.date = date

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.date}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

    def parse(self, response: httpx.Response) -> list[base_types.StatDict]:
        selector = Selector(response.text)
        matches: list[base_types.StatDict] = []

        competitions_id = "|".join(
            (
                comptition_params_dict["fbref_id"]
                for comptition_params_dict in COMPETITIONS.values()
            )
        )
        tables = selector.xpath(
            f"//table[re:test(@id, 'sched_.*_({competitions_id})\\b')]"
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
                id_ = href.split("/")[3]
                matches.append(
                    base_types.StatDict(
                        id=id_,
                        name=f"{home_name} vs {away_name}",
                    )
                )
            except ValueError:
                pass
        return matches


class Match(Spider):
    def __init__(self, *, id: str) -> None:
        self.id = id

    @property
    def request(self) -> httpx.Request:
        path = f"/matches/{self.id}"
        return httpx.Request("GET", url=f"{BASE_URL}{path}")

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
