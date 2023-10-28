from pathlib import Path

import pytest
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders.fbref import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)

pytestmark = pytest.mark.asyncio


def mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    httpx_mock.add_response(
        url=f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}",
        text=text,
    )


async def test_competitions(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("comps_.html", httpx_mock)
    spider = Competitions(client=client)
    coms = await spider.download()
    assert coms[0].name == "Premier League"


async def test_competition(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("comps_9_Premier-League-Stats.html", httpx_mock)
    spider = Competition(id="9", path_name="Premier-League", client=client)
    com = await spider.download()
    assert com.name == "Premier League"


async def test_team(httpx_mock: HTTPXMock, client: httpx.AsyncClient) -> None:
    mock("squads_18bb7c10_Arsenal-Stats.html", httpx_mock)
    spider = Team(id="18bb7c10", path_name="Arsenal", client=client)
    team = await spider.download()
    assert team.name == "Arsenal"
    assert int(team.shooting.xg) == int(8.3)


async def test_member(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("players_bc7dc64d_Bukayo-Saka.html", httpx_mock)
    spider = Member(id="bc7dc64d", path_name="Bukayo-Saka", client=client)
    member = await spider.download()
    assert member.name == "Bukayo Saka"


async def test_matches(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("matches_2023-09-03.html", httpx_mock)
    spider = Matches(date="2023-09-03", client=client)
    matches = await spider.download()
    match = matches[0]
    assert match.id == "bdbc722e"
    assert match.name == "Liverpool vs Aston Villa"


async def test_match(httpx_mock: HTTPXMock, client: httpx.AsyncClient) -> None:
    mock("matches_74125d47.html", httpx_mock)
    spider = Match(id="74125d47", client=client)
    match = await spider.download()
    assert match.name == "Arsenal vs Manchester United"
