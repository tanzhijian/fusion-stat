import typing

import pytest_asyncio
import respx

from fusion_stat import Fusion, Matches
from tests.utils import fbref_mock, fotmob_mock


class TestMatches:
    @pytest_asyncio.fixture(scope="class")
    async def matches(
        self, fusion: Fusion
    ) -> typing.AsyncGenerator[Matches, typing.Any]:
        fotmob_mock("matches?date=20230903.json")
        fbref_mock("matches_2023-09-03.html")

        with respx.mock:
            matches = await fusion.get_matches(date="2023-09-03")
        yield matches

    def test_get(self, matches: Matches) -> None:
        assert len(matches.fotmob) == len(matches.fbref) + 1

        match_1 = matches.fotmob[0]
        assert match_1.id == "4193495"
        assert match_1.name == "Crystal Palace vs Wolverhampton Wanderers"

        match_2 = matches.fbref[0]
        assert match_2.id == "bdbc722e"
        assert match_2.name == "Liverpool vs Aston Villa"

    def test_info(self, matches: Matches) -> None:
        info = matches.info
        match = info["matches"][0]
        assert match["name"] == "Crystal Palace vs Wolverhampton Wanderers"
        assert match["score"] == "3 - 2"

    def test_index(self, matches: Matches) -> None:
        index = matches.index()
        assert len(index) == 18
        params = index[0]
        assert params["fotmob_id"] == "4193495"
        assert params["fbref_id"] == "f9436d32"
