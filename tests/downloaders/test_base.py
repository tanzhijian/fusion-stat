import pytest
from pytest_httpx import HTTPXMock
import httpx

from fusion_stat.downloaders.base import Spider


pytestmark = pytest.mark.asyncio


class Foo(Spider):
    module_name = "base"

    def parse(self, response: httpx.Response) -> str:
        return "foo"

    async def download(self) -> str:
        url = "https://tanzhijian.org"
        response = await self.get(url)
        return self.parse(response)


async def test_spider(httpx_mock: HTTPXMock) -> None:
    assert Foo.module_name == "base"

    httpx_mock.add_response(url="https://url.url", json={"foo": "bar"})
    httpx_mock.add_response(url="https://url.url/404", status_code=404)

    async with Foo(client=httpx.AsyncClient()) as spider:
        response = await spider.get("https://url.url")
        assert response.json()["foo"] == "bar"

        with pytest.raises(httpx.HTTPStatusError):
            response = await spider.get("https://url.url/404")
            assert response.status_code == 404

    with pytest.raises(RuntimeError):
        response = await spider.get("https://url.url")

    spider2 = Foo(client=httpx.AsyncClient())
    response = await spider2.get("https://url.url")
    assert response.json()["foo"] == "bar"
    await spider2.aclose()

    with pytest.raises(RuntimeError):
        response = await spider2.get("https://url.url")
