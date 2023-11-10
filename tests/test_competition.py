import typing

import httpx
import pytest_asyncio
import respx

from .utils import fotmob_mock, fbref_mock, premier_league_mock
from fusion_stat.competition import Fusion, Competition


@pytest_asyncio.fixture(scope="module")
async def fusion(
    client: httpx.AsyncClient,
) -> typing.AsyncGenerator[Fusion, typing.Any]:
    fotmob_mock("leagues?id=47.json")
    fbref_mock("comps_9_Premier-League-Stats.html")
    premier_league_mock(
        "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json"
    )

    com = Competition(
        fotmob_id="47",
        fbref_id="9",
        fbref_path_name="Premier-League",
        official_name="Premier League",
        client=client,
    )
    with respx.mock:
        fusion = await com.gather()
    yield fusion


def test_get(fusion: Fusion) -> None:
    assert fusion.fotmob.name == "Premier League"


def test_info(fusion: Fusion) -> None:
    info = fusion.info
    assert info["name"] == "Premier League"
    assert "Premier League" in info["names"]
    assert info["logo"]


def test_teams(fusion: Fusion) -> None:
    teams = fusion.teams
    assert len(teams) == 20
    team = teams[0]
    assert team["name"] == "Manchester City"
    assert int(team["shooting"]["xg"]) == int(8.6)
    assert (
        team["logo"]
        == "https://resources.premierleague.com/premierleague/badges/rb/t43.svg"
    )


def test_matches(fusion: Fusion) -> None:
    matches = fusion.matches
    assert len(matches) == 380
    match = matches[0]
    assert match["score"] == "0 - 3"


def test_teams_index(fusion: Fusion) -> None:
    index = fusion.teams_index()
    assert len(index) == 20
    assert index[0]["fotmob_id"] == "8456"


def test_table(fusion: Fusion) -> None:
    table = fusion.table
    city = table[0]
    assert city["name"] == "Manchester City"
    assert city["draws"] == 0
    assert city["goals_for"] == 11
    assert int(city["xg"]) == int(8.6)

    chelsea = table[11]
    assert chelsea["name"] == "Chelsea"
    assert chelsea["played"] == 4
    assert chelsea["losses"] == 2
    assert chelsea["goals_against"] == 5
    assert chelsea["points"] == 4
    assert int(chelsea["xg"]) == int(8.3)
