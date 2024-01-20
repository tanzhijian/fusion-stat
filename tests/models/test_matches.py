import httpx
import pytest

from fusion_stat import Matches
from fusion_stat.spiders import fbref, fotmob
from fusion_stat.types import base_types
from tests.utils import read_data


class TestMatches:
    @pytest.fixture(scope="class")
    def matches(self, client: httpx.AsyncClient) -> Matches:
        fotmob_data = read_data("fotmob", "matches?date=20230903.json")
        fbref_data = read_data("fbref", "matches_2023-09-03.html")

        fotmob_spider = fotmob.Matches(date="2023-09-03", client=client)
        fbref_spider = fbref.Matches(date="2023-09-03", client=client)

        return Matches(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
            fbref=fbref_spider.parse(httpx.Response(200, text=fbref_data)),
        )

    def test_most_similar_team(self, matches: Matches) -> None:
        query: base_types.StatDict = {"id": "1", "name": "ab"}
        choices: list[base_types.StatDict] = [
            {"id": "2", "name": "abc"},
            {"id": "3", "name": "c"},
        ]
        result = matches._most_similar_match(query, choices)
        assert result["id"] == "2"

    def test_items(self, matches: Matches) -> None:
        match = matches.items[0]
        assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
        assert match["home"]["score"] == 3
        assert match["away"]["score"] == 2

    def test_info(self, matches: Matches) -> None:
        assert matches.info["count"] == 19

    def test_get_params(self, matches: Matches) -> None:
        params = matches.get_params()
        # 有一场比赛取消了（马竞）导致生成的 params 少一场
        # 还没有踢的比赛 fbref 没有 id
        assert len(params) == 18
        match = params[0]
        assert match["fotmob_id"] == "4193495"
        assert match["fbref_id"] == "f9436d32"
