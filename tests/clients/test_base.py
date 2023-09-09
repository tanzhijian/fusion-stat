import pytest
from pytest_httpx import HTTPXMock

from fusion_stat.clients.base import JSONClient, HTMLClient


pytestmark = pytest.mark.asyncio


async def test_json_client(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"foo": "bar"})
    async with JSONClient() as client:
        response = await client.get("https://url.url")
        assert response["foo"] == "bar"


async def test_html_client(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(text="foo")
    async with HTMLClient() as client:
        response = await client.get("https://url.url")
        assert response == "foo"
