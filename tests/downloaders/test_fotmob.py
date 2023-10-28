import json
from pathlib import Path

import httpx
import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders.fotmob import (
    Competitions,
    Competition,
    Team,
    Member,
    Matches,
    Match,
)


pytestmark = pytest.mark.asyncio


def mock(file: str, httpx_mock: HTTPXMock) -> None:
    with open(Path(f"tests/data/fotmob/{file}")) as f:
        data = json.load(f)
    httpx_mock.add_response(
        url=f"https://www.fotmob.com/api/{file.split('.')[0]}",
        json=data,
    )


async def test_competitions(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("allLeagues.json", httpx_mock)
    spider = Competitions(client=client)
    coms = await spider.download()
    assert coms[0].name == "Premier League"


async def test_competition(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("leagues?id=47.json", httpx_mock)
    spider = Competition(id="47", client=client)
    com = await spider.download()
    assert com.name == "Premier League"


async def test_team(httpx_mock: HTTPXMock, client: httpx.AsyncClient) -> None:
    mock("teams?id=9825.json", httpx_mock)
    spider = Team(id="9825", client=client)
    team = await spider.download()
    assert team.name == "Arsenal"


async def test_member(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("playerData?id=961995.json", httpx_mock)
    spider = Member(id="961995", client=client)
    member = await spider.download()
    assert member.name == "Bukayo Saka"


async def test_matches(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    mock("matches?date=20230903.json", httpx_mock)
    spider = Matches(date="2023-09-03", client=client)
    matches = await spider.download()
    match = matches[0]
    assert match.id == "4193495"
    assert match.name == "Crystal Palace vs Wolverhampton Wanderers"


async def test_match(httpx_mock: HTTPXMock, client: httpx.AsyncClient) -> None:
    mock("matchDetails?matchId=4193490.json", httpx_mock)
    spider = Match(id="4193490", client=client)
    match = await spider.download()
    assert match.name == "Arsenal vs Manchester United"
