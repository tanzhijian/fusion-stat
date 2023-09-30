import pytest
from pytest_httpx import HTTPXMock
import httpx

from fusion_stat.downloaders.base import Downloader


pytestmark = pytest.mark.asyncio


async def test_client(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://url.url", json={"foo": "bar"})
    httpx_mock.add_response(url="https://url.url/404", status_code=404)
    async with Downloader(httpx.AsyncClient()) as downloader:
        response = await downloader.get("https://url.url")
        assert response.json()["foo"] == "bar"

        with pytest.raises(httpx.HTTPStatusError):
            response = await downloader.get("https://url.url/404")
            assert response.status_code == 404

    with pytest.raises(RuntimeError):
        response = await downloader.get("https://url.url")

    downloader2 = Downloader(httpx.AsyncClient())
    response = await downloader2.get("https://url.url")
    assert response.json()["foo"] == "bar"
    await downloader2.aclose()

    with pytest.raises(RuntimeError):
        response = await downloader2.get("https://url.url")
