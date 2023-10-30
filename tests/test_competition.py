import typing

import httpx
import pytest_asyncio
import respx

from .spiders.test_fotmob import mock as fotmob_mock
from .spiders.test_fbref import mock as fbref_mock
from fusion_stat.competition import Response, Competition
from fusion_stat.models import Params


@pytest_asyncio.fixture(scope="module")
async def response(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Response, typing.Any]:
    fotmob_mock("leagues?id=47.json")
    fbref_mock("comps_9_Premier-League-Stats.html")

    params = Params(
        fotmob_id="47",
        fbref_id="9",
        fbref_path_name="Premier-League",
    )
    com = Competition(params, client=client)
    with respx.mock:
        response = await com.get()
    yield response


def test_get(response: Response) -> None:
    assert response.fotmob.name == "Premier League"


def test_info(response: Response) -> None:
    info = response.info
    assert info["name"] == "Premier League"
    assert "Premier League" in info["names"]


def test_teams(response: Response) -> None:
    teams = response.teams
    assert len(teams) == 20
    assert teams[0]["shooting"]["xg"] == 8.6


def test_matches(response: Response) -> None:
    matches = response.matches
    assert len(matches) == 380
    match = matches[0]
    assert match["score"] == "0 - 3"


def test_teams_index(response: Response) -> None:
    index = response.teams_index()
    assert len(index) == 20
    assert index[0].fotmob_id == "8456"


def test_table(response: Response) -> None:
    table = response.table
    city = table[0]
    assert city["name"] == "Manchester City"
    assert city["draws"] == 0
    assert city["goals_for"] == 11
    assert city["xg"] == 8.6

    chelsea = table[11]
    assert chelsea["name"] == "Chelsea"
    assert chelsea["played"] == 4
    assert chelsea["losses"] == 2
    assert chelsea["goals_against"] == 5
    assert chelsea["points"] == 4
    assert chelsea["xg"] == 8.3
