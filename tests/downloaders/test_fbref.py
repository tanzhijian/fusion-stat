from pathlib import Path

import httpx
import pytest
import respx

from fusion_stat.downloaders.fbref import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)

pytestmark = pytest.mark.asyncio


def mock(file: str) -> None:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    respx.get(
        f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, text=text))


@respx.mock
async def test_competitions(client: httpx.AsyncClient) -> None:
    mock("comps_.html")
    spider = Competitions(client=client)
    coms = await spider.download()
    assert coms[0].name == "Premier League"


@respx.mock
async def test_competition(client: httpx.AsyncClient) -> None:
    mock("comps_9_Premier-League-Stats.html")
    spider = Competition(id="9", path_name="Premier-League", client=client)
    com = await spider.download()
    assert com.name == "Premier League"


@respx.mock
async def test_team(client: httpx.AsyncClient) -> None:
    mock("squads_18bb7c10_Arsenal-Stats.html")
    spider = Team(id="18bb7c10", path_name="Arsenal", client=client)
    team = await spider.download()
    assert team.name == "Arsenal"
    assert int(team.shooting.xg) == int(8.3)


@respx.mock
async def test_member(client: httpx.AsyncClient) -> None:
    mock("players_bc7dc64d_Bukayo-Saka.html")
    spider = Member(id="bc7dc64d", path_name="Bukayo-Saka", client=client)
    member = await spider.download()
    assert member.name == "Bukayo Saka"


@respx.mock
async def test_matches(client: httpx.AsyncClient) -> None:
    mock("matches_2023-09-03.html")
    spider = Matches(date="2023-09-03", client=client)
    matches = await spider.download()
    match = matches[0]
    assert match.id == "bdbc722e"
    assert match.name == "Liverpool vs Aston Villa"


@respx.mock
async def test_match(client: httpx.AsyncClient) -> None:
    mock("matches_74125d47.html")
    spider = Match(id="74125d47", client=client)
    match = await spider.download()
    assert match.name == "Arsenal vs Manchester United"
