import typing

import httpx
import pytest
import respx

from fusion_stat.scraper import BaseSpider, Downloader, Engine

response_json = httpx.Response(200, json={"name": "json"})
response_text = httpx.Response(200, text="text")
JSON_URL = "https://example.com/json"
TEXT_URL = "https://example.com/text"


class SpiderJSON(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", JSON_URL)

    def parse(self, response: httpx.Response) -> typing.Any:
        json = response.json()
        return json["name"]


class SpiderText(BaseSpider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", TEXT_URL)

    def parse(self, response: httpx.Response) -> typing.Any:
        return response.text


class TestDownloader:
    @pytest.fixture(scope="class")
    def downloader(self, client: httpx.AsyncClient) -> Downloader:
        return Downloader(client=client)

    @pytest.mark.anyio
    async def test_get(self, downloader: Downloader) -> None:
        request = SpiderJSON().request
        respx.get(JSON_URL).mock(return_value=response_json)
        with respx.mock:
            response = await downloader._get(request)
            json = response.json()
            assert json["name"] == "json"

    @pytest.mark.anyio
    async def test_download(self, downloader: Downloader) -> None:
        request_json = SpiderJSON().request
        request_text = SpiderText().request
        respx.get(JSON_URL).mock(return_value=response_json)
        respx.get(TEXT_URL).mock(return_value=response_text)
        with respx.mock:
            r1, r2 = await downloader.download(request_json, request_text)
            json = r1.json()
            assert json["name"] == "json"
            text = r2.text
            assert text == "text"


class TestEngine:
    @pytest.fixture(scope="class")
    async def engine(self) -> typing.AsyncGenerator[Engine, typing.Any]:
        engine = Engine()
        yield engine
        await engine.close()
        assert engine.downloader.client.is_closed

    @pytest.mark.anyio
    async def test_process(self, engine: Engine) -> None:
        spider = SpiderText()
        respx.get(TEXT_URL).mock(return_value=response_text)
        with respx.mock:
            (text,) = await engine.process(spider)
            assert text == "text"
