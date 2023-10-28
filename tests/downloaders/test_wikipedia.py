import pytest
import httpx
from pytest_httpx import HTTPXMock

from fusion_stat.downloaders.wikipedia import Competition

pytestmark = pytest.mark.asyncio


async def test_competition(
    httpx_mock: HTTPXMock, client: httpx.AsyncClient
) -> None:
    httpx_mock.add_response(
        url="https://en.wikipedia.org/wiki/2023-24_Premier_League", text="halo"
    )
    spider = Competition(id="Premier_League", client=client)
    com = await spider.download()
    assert com == "competition"
