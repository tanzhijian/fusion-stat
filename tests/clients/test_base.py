import pytest
from pytest_httpx import HTTPXMock
from httpx import HTTPStatusError

from fusion_stat.clients.base import Client


pytestmark = pytest.mark.asyncio


async def test_client(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://url.url", json={"foo": "bar"})
    httpx_mock.add_response(url="https://url.url/404", status_code=404)
    async with Client() as client:
        response = await client.get("https://url.url")
        assert response.json()["foo"] == "bar"

        with pytest.raises(HTTPStatusError):
            response = await client.get("https://url.url/404")
            assert response.status_code == 404

    with pytest.raises(RuntimeError):
        response = await client.get("https://url.url")

    client2 = Client()
    response = await client2.get("https://url.url")
    assert response.json()["foo"] == "bar"
    await client2.aclose()

    with pytest.raises(RuntimeError):
        response = await client2.get("https://url.url")
