import typing

import httpx
import pytest
import respx


from fusion_stat.base import Spider, Fusion


pytestmark = pytest.mark.asyncio


class Foo(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", "https://tanzhijian.org")

    def parse(self, response: httpx.Response) -> str:
        return "foo"


class Bar(Fusion[str]):
    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (Foo,)

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(client=client, **self.kwargs)
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> str:
        return "bar"


@respx.mock
async def test_spider_get() -> None:
    respx.get("https://url.url").mock(
        return_value=httpx.Response(200, json={"foo": "bar"})
    )

    request = httpx.Request("GET", "https://url.url")

    async with Foo(client=httpx.AsyncClient()) as spider:
        response = await spider.get(request)
        assert response.json()["foo"] == "bar"

    with pytest.raises(RuntimeError):
        response = await spider.get(request)

    spider2 = Foo(client=httpx.AsyncClient())
    response = await spider2.get(request)
    assert response.json()["foo"] == "bar"
    await spider2.aclose()

    with pytest.raises(RuntimeError):
        response = await spider2.get(request)


@respx.mock
async def test_spider_bad_get(client: httpx.AsyncClient) -> None:
    respx.get("https://example.org/").mock(side_effect=[httpx.Response(404)])
    spider = Foo(client=client)
    request = httpx.Request("GET", "https://example.org/")
    with pytest.raises(httpx.HTTPStatusError):
        response = await spider.get(request)
        assert response.status_code == 404


@respx.mock
async def test_spider_download(client: httpx.AsyncClient) -> None:
    route = respx.get("https://tanzhijian.org")
    spider = Foo(client=client)
    response = await spider.download()
    assert response == "foo"
    assert route.called


@respx.mock
async def test_fusion_get() -> None:
    route = respx.get("https://tanzhijian.org")
    bar = Bar()
    response = await bar.get()
    assert route.called
    assert response == "bar"
