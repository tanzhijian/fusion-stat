import httpx
import pytest

from fusion_stat import Matches
from fusion_stat.scraper import BaseItem
from fusion_stat.spiders import fotmob
from tests.utils import read_data


class TestMatches:
    @pytest.fixture(scope="class")
    def matches(self) -> Matches:
        fotmob_data = read_data("fotmob", "matches?date=20230903.json")

        fotmob_spider = fotmob.matches.Spider(date="2023-09-03")

        return Matches(
            fotmob=fotmob_spider.parse(httpx.Response(200, json=fotmob_data)),
        )

    def test_find_team(self, matches: Matches) -> None:
        query = BaseItem(**{"id": "1", "name": "ab"})
        choices = [
            BaseItem(**{"id": "2", "name": "abc"}),
            BaseItem(**{"id": "3", "name": "c"}),
        ]
        result = matches._find_match(query, choices)
        assert result.id == "2"

    def test_get_items(self, matches: Matches) -> None:
        items = matches.get_items()
        match = next(items)
        assert match["id"] == "4193495"
        assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
        assert match["home"]["score"] == 3
        assert match["away"]["score"] == 2

    def test_items(self, matches: Matches) -> None:
        assert len(matches.items) == 19

    def test_info(self, matches: Matches) -> None:
        assert matches.info["count"] == 19

    def test_get_params(self, matches: Matches) -> None:
        params = list(matches.get_params())
        # 有一场比赛取消了（马竞）导致生成的 params 少一场
        # 还没有踢的比赛 fbref 没有 id
        # 暂时去除了 fbref 的数据所以数量与上面一致
        assert len(params) == 19
        match = params[0]
        assert match["fotmob_id"] == "4193495"
