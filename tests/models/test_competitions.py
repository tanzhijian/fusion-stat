import typing

import httpx
import pytest
import pytest_asyncio
import respx

from fusion_stat import Competitions, Fusion
from tests.utils import fbref_mock, fotmob_mock


class TestCompetitions:
    @pytest_asyncio.fixture(scope="class")
    async def competitions(
        self,
        client: httpx.AsyncClient,
    ) -> typing.AsyncGenerator[Competitions, typing.Any]:
        fotmob_mock("allLeagues.json")
        fbref_mock("comps_.html")

        fusion = Fusion(client=client)
        with respx.mock:
            coms = await fusion.get_competitions()
        yield coms

    def test_get(self, competitions: Competitions) -> None:
        assert len(competitions.fotmob) > 0

    def test_index(self, competitions: Competitions) -> None:
        index = competitions.index()
        competition = index[0]
        assert competition["fbref_path_name"] == "Premier-League"
        assert competition["official_name"] == "Premier League"
        with pytest.raises(KeyError):
            assert competition["season"]
