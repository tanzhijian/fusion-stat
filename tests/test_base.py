import httpx
import pytest
import respx


from fusion_stat.base import Spider


pytestmark = pytest.mark.asyncio


class Foo(Spider):
    @property
    def request(self) -> httpx.Request:
        return httpx.Request("GET", "https://tanzhijian.org")

    def parse(self, response: httpx.Response) -> str:
        return "foo"


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
async def test_spider_download(client: httpx.AsyncClient) -> None:
    route = respx.get("https://tanzhijian.org")
    spider = Foo(client=client)
    response = await spider.download()
    assert response == "foo"
    assert route.called
