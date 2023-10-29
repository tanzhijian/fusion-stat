import httpx
import pytest
import respx

from fusion_stat.downloaders.wikipedia import Competition

pytestmark = pytest.mark.asyncio


@respx.mock
async def test_competition(client: httpx.AsyncClient) -> None:
    respx.get("https://en.wikipedia.org/wiki/2023-24_Premier_League")
    spider = Competition(id="Premier_League", client=client)
    com = await spider.download()
    assert com == "competition"
