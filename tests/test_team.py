import typing

import httpx
import pytest_asyncio
import respx

from .spiders.test_fotmob import mock as fotmob_mock
from .spiders.test_fbref import mock as fbref_mock
from fusion_stat.team import Response, Team
from fusion_stat.models import Params


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("teams?id=9825.json")
    fbref_mock("squads_18bb7c10_Arsenal-Stats.html")

    params = Params(
        fotmob_id="9825",
        fbref_id="18bb7c10",
        fbref_path_name="Arsenal",
    )
    team = Team(params, client=client)
    with respx.mock:
        response = await team.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Arsenal"
    assert response.fbref.shooting.xg == 8.3

    assert len(response.fotmob.members) == 26
    coach = response.fotmob.members[0]
    assert coach.is_staff
    player = response.fotmob.members[1]
    assert not player.is_staff
    assert player.position == "GK"
    assert player.country == "Spain"

    saka = response.fbref.members[4]
    assert saka.position == "FW"
    assert saka.country_code == "ENG"
    assert saka.path_name == "Bukayo-Saka"
    assert int(saka.shooting.shots) == 11


def test_staff(response: Response) -> None:
    staff = response.staff
    assert staff[0]["name"] == "Mikel Arteta"
    assert staff[0]["country"] == "Spain"


def test_players(response: Response) -> None:
    players = response.players
    assert len(players) == 23
    martin = players[-1]
    assert martin["name"] == "Gabriel Martinelli"
    assert "Gabriel Martinelli" in martin["names"]


def test_members_index(response: Response) -> None:
    index = response.members_index()
    params = index[0]
    assert params.fotmob_id == "562727"
    assert params.fbref_id == "98ea5115"
    assert params.fbref_path_name == "David-Raya"
