from pathlib import Path

import pytest
import httpx_file

from fusion_stat.clients.base import JSONClient, HTMLClient


pytestmark = pytest.mark.asyncio
FOO = Path(Path.cwd(), "tests/data/foo.json").as_uri()


async def test_json_client() -> None:
    async with JSONClient(httpx_file.AsyncClient) as client:
        response = await client.get(FOO)
        assert response["foo"] == "bar"


async def test_html_client() -> None:
    async with HTMLClient(httpx_file.AsyncClient) as client:
        response = await client.get(FOO)
        assert response[0] == "{"
