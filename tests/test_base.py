import httpx
import pytest
import respx


from fusion_stat.base import Spider


pytestmark = pytest.mark.asyncio


class Foo(Spider):
    module_name = "base"

    def parse(self, response: httpx.Response) -> str:
        return "foo"

    async def download(self) -> str:
        url = "https://tanzhijian.org"
        response = await self.get(url)
        return self.parse(response)


@respx.mock
async def test_spider() -> None:
    assert Foo.module_name == "base"

    respx.get("https://url.url").mock(
        return_value=httpx.Response(200, json={"foo": "bar"})
    )

    async with Foo(client=httpx.AsyncClient()) as spider:
        response = await spider.get("https://url.url")
        assert response.json()["foo"] == "bar"

    with pytest.raises(RuntimeError):
        response = await spider.get("https://url.url")

    spider2 = Foo(client=httpx.AsyncClient())
    response = await spider2.get("https://url.url")
    assert response.json()["foo"] == "bar"
    await spider2.aclose()

    with pytest.raises(RuntimeError):
        response = await spider2.get("https://url.url")
