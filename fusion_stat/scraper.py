import asyncio
import typing
from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel


class BaseSpider(ABC):
    @property
    @abstractmethod
    def request(self) -> httpx.Request:
        ...

    @abstractmethod
    def parse(self, response: httpx.Response) -> typing.Any:
        ...


class BaseItem(BaseModel):
    id: str
    name: str


class Downloader:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
    ):
        if client is None:
            self.client = httpx.AsyncClient()
        else:
            self.client = client

    async def _get(self, request: httpx.Request) -> httpx.Response:
        response = await self.client.send(request)
        response.raise_for_status()
        return response

    async def download(self, *requests: httpx.Request) -> list[httpx.Response]:
        tasks = (self._get(request) for request in requests)
        responses = await asyncio.gather(*tasks)
        return responses


class Engine:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.downloader = Downloader(client=client)

    async def process(self, *spiders: BaseSpider) -> list[typing.Any]:
        items = []
        requests = (spider.request for spider in spiders)
        responses = await self.downloader.download(*requests)
        for spider, response in zip(spiders, responses):
            item = spider.parse(response)
            items.append(item)
        return items

    async def close(self) -> None:
        await self.downloader.client.aclose()
