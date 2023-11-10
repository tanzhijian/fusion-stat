import typing

import httpx
import pytest
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.competitions import Fusion, Competitions


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("allLeagues.json")
    fbref_mock("comps_.html")

    coms = Competitions(client=client)
    with respx.mock:
        fusion = await coms.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert len(fusion.fotmob) > 0


def test_index(fusion: Fusion) -> None:
    index = fusion.index()
    competition = index[0]
    assert competition["fbref_path_name"] == "Premier-League"
    assert competition["official_name"] == "Premier League"
    with pytest.raises(KeyError):
        assert competition["season"]
