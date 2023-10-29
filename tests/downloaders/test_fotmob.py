import json
from pathlib import Path

import httpx
import pytest
import respx

from fusion_stat.downloaders.fotmob import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)


pytestmark = pytest.mark.asyncio


def mock(file: str) -> None:
    with open(Path(f"tests/data/fotmob/{file}")) as f:
        data = json.load(f)
    respx.get(url=f"https://www.fotmob.com/api/{file.split('.')[0]}").mock(
        httpx.Response(200, json=data)
    )


@respx.mock
async def test_competitions(client: httpx.AsyncClient) -> None:
    mock("allLeagues.json")
    spider = Competitions(client=client)
    coms = await spider.download()
    assert coms[0].name == "Premier League"


@respx.mock
async def test_competition(client: httpx.AsyncClient) -> None:
    mock("leagues?id=47.json")
    spider = Competition(id="47", client=client)
    com = await spider.download()
    assert com.name == "Premier League"


@respx.mock
async def test_team(client: httpx.AsyncClient) -> None:
    mock("teams?id=9825.json")
    spider = Team(id="9825", client=client)
    team = await spider.download()
    assert team.name == "Arsenal"


@respx.mock
async def test_member(client: httpx.AsyncClient) -> None:
    mock("playerData?id=961995.json")
    spider = Member(id="961995", client=client)
    member = await spider.download()
    assert member.name == "Bukayo Saka"


@respx.mock
async def test_matches(client: httpx.AsyncClient) -> None:
    mock("matches?date=20230903.json")
    spider = Matches(date="2023-09-03", client=client)
    matches = await spider.download()
    match = matches[0]
    assert match.id == "4193495"
    assert match.name == "Crystal Palace vs Wolverhampton Wanderers"


@respx.mock
async def test_match(client: httpx.AsyncClient) -> None:
    mock("matchDetails?matchId=4193490.json")
    spider = Match(id="4193490", client=client)
    match = await spider.download()
    assert match.name == "Arsenal vs Manchester United"
