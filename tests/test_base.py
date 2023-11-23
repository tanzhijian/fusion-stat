import typing

import httpx
import pytest
import respx

from fusion_stat.base import Collector, Spider

pytestmark = pytest.mark.asyncio


class SpiderTest(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", "https://tanzhijian.org")

    def parse(self, response: httpx.Response) -> str:
        return "foo"


class CollectorTest(Collector[str]):
    @property
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        return (SpiderTest(client=self.client).process(),)

    def parse(self, responses: list[typing.Any]) -> str:
        return "bar"


@respx.mock
async def test_spider_get() -> None:
    respx.get("https://url.url").mock(
        return_value=httpx.Response(200, json={"foo": "bar"})
    )

    request = httpx.Request("GET", "https://url.url")

    async with SpiderTest(client=httpx.AsyncClient()) as spider:
        response = await spider.get(request)
        assert response.json()["foo"] == "bar"

    with pytest.raises(RuntimeError):
        response = await spider.get(request)

    spider2 = SpiderTest(client=httpx.AsyncClient())
    response = await spider2.get(request)
    assert response.json()["foo"] == "bar"
    await spider2.aclose()

    with pytest.raises(RuntimeError):
        response = await spider2.get(request)


@respx.mock
async def test_spider_bad_get(client: httpx.AsyncClient) -> None:
    respx.get("https://example.org/").mock(side_effect=[httpx.Response(404)])
    spider = SpiderTest(client=client)
    request = httpx.Request("GET", "https://example.org/")
    with pytest.raises(httpx.HTTPStatusError):
        response = await spider.get(request)
        assert response.status_code == 404


@respx.mock
async def test_spider_process(client: httpx.AsyncClient) -> None:
    route = respx.get("https://tanzhijian.org")
    spider = SpiderTest(client=client)
    response = await spider.process()
    assert response == "foo"
    assert route.called


@respx.mock
async def test_gather_get(client: httpx.AsyncClient) -> None:
    route = respx.get("https://tanzhijian.org")
    collector1 = CollectorTest()
    assert not collector1.has_client
    response1 = await collector1.gather()
    assert route.called
    assert response1 == "bar"
    assert collector1.client.is_closed

    collector2 = CollectorTest(client=client)
    assert collector2.has_client
    response2 = await collector2.gather()
    assert route.call_count == 2
    assert response2 == "bar"
    assert not collector2.client.is_closed
