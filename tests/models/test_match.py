import typing

import pytest_asyncio
import respx

from fusion_stat import Fusion, Match
from tests.utils import fbref_mock, fotmob_mock


class TestMatch:
    @pytest_asyncio.fixture(scope="class")
    async def match(
        self, fusion: Fusion
    ) -> typing.AsyncGenerator[Match, typing.Any]:
        fotmob_mock("matchDetails?matchId=4193490.json")
        fbref_mock("matches_74125d47.html")

        with respx.mock:
            match = await fusion.get_match(
                fotmob_id="4193490", fbref_id="74125d47"
            )
        yield match

    def test_get(self, match: Match) -> None:
        assert match.fotmob.name == "Arsenal vs Manchester United"
        assert match.fbref.name == "Arsenal vs Manchester United"
