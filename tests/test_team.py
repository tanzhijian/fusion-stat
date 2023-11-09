import typing

import httpx
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock
from fusion_stat.team import Fusion, Team


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("teams?id=9825.json")
    fbref_mock("squads_18bb7c10_Arsenal-Stats.html")

    params = {
        "fotmob_id": "9825",
        "fbref_id": "18bb7c10",
        "fbref_path_name": "Arsenal",
    }
    team = Team(**params, client=client)
    with respx.mock:
        fusion = await team.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert fusion.fotmob.name == "Arsenal"
    assert int(fusion.fbref.shooting.xg) == int(8.3)

    assert len(fusion.fotmob.members) == 26
    coach = fusion.fotmob.members[0]
    assert coach.is_staff
    player = fusion.fotmob.members[1]
    assert not player.is_staff
    assert player.position == "GK"
    assert player.country == "Spain"

    saka = fusion.fbref.members[4]
    assert saka.position == "FW"
    assert saka.country_code == "ENG"
    assert saka.path_name == "Bukayo-Saka"
    assert int(saka.shooting.shots) == 11


def test_staff(fusion: Fusion) -> None:
    staff = fusion.staff
    assert staff[0]["name"] == "Mikel Arteta"
    assert staff[0]["country"] == "Spain"


def test_players(fusion: Fusion) -> None:
    players = fusion.players
    assert len(players) == 23
    martin = players[-1]
    assert martin["name"] == "Gabriel Martinelli"
    assert "Gabriel Martinelli" in martin["names"]


def test_members_index(fusion: Fusion) -> None:
    index = fusion.members_index()
    params = index[0]
    assert params["fotmob_id"] == "562727"
    assert params["fbref_id"] == "98ea5115"
    assert params["fbref_path_name"] == "David-Raya"
