import httpx
import pytest
import respx

from fusion_stat.base import Downloader, Spider


class DownloaderTest(Downloader):
    pass


@pytest.mark.anyio
async def test_downloader() -> None:
    downloader = DownloaderTest()
    assert not downloader.client.is_closed
    await downloader.aclose()
    assert downloader.client.is_closed


@pytest.mark.anyio
async def test_downloader_include_client() -> None:
    downloader = DownloaderTest(client=httpx.AsyncClient(params={"a": "b"}))
    assert downloader.client.params["a"] == "b"
    assert not downloader.client.is_closed
    await downloader.aclose()
    assert downloader.client.is_closed


@pytest.mark.anyio
async def test_downloader_context() -> None:
    async with DownloaderTest() as downloader:
        assert not downloader.client.is_closed
    assert downloader.client.is_closed


class SpiderTest(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", "https://example.org/")

    def parse(self, response: httpx.Response) -> str:
        return "foo"


class TestSpider:
    @pytest.fixture(scope="class")
    def spider(self, client: httpx.AsyncClient) -> Spider:
        return SpiderTest(client=client)

    @pytest.mark.anyio
    @respx.mock
    async def test_get(self, spider: Spider) -> None:
        respx.get("https://example.org/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        response = await spider.get(spider.request)
        assert response.json()["foo"] == "bar"

    @pytest.mark.anyio
    @respx.mock
    async def test_bad_get(self, spider: Spider) -> None:
        respx.get("https://example.org/").mock(
            side_effect=[httpx.Response(404)]
        )

        with pytest.raises(httpx.HTTPStatusError):
            response = await spider.get(spider.request)
            assert response.status_code == 404

    @pytest.mark.anyio
    @respx.mock
    async def test_spider_process(self, spider: Spider) -> None:
        route = respx.get("https://example.org/")
        response = await spider.process()
        assert response == "foo"
        assert route.called
