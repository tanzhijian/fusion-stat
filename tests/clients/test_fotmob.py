import json as json
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.clients import FotMob


pytestmark = pytest.mark.asyncio


async def test_get_competition(httpx_mock: HTTPXMock) -> None:
    with open(Path("tests/data/fotmob/leagues_pl.json")) as f:
        data = json.load(f)
    httpx_mock.add_response(
        url="https://www.fotmob.com/api/leagues?id=47",
        json=data,
    )

    async with FotMob() as fm:
        pl = await fm.get_competition("47")
    assert pl["seostr"] == "premier-league"
