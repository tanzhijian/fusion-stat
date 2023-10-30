import asyncio
import typing
from abc import ABC, abstractmethod
from types import TracebackType

import httpx


T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Spider(ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
    ) -> None:
        self.client = client

    module_name: str

    async def aclose(self) -> None:
        await self.client.aclose()

    async def __aenter__(self: U) -> U:
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_value: typing.Optional[BaseException] = None,
        traceback: typing.Optional[TracebackType] = None,
    ) -> None:
        await self.aclose()

    async def get(self, url: str, **kwargs: typing.Any) -> httpx.Response:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    def parse(self, response: httpx.Response) -> typing.Any:
        ...

    @abstractmethod
    async def download(self) -> typing.Any:
        ...


class Fusion(typing.Generic[T], ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        self.client = client
        self.kwargs = kwargs

    @property
    @abstractmethod
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        ...

    @abstractmethod
    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        ...

    @abstractmethod
    def parse(self, responses: list[typing.Any]) -> T:
        ...

    async def get(self) -> T:
        if self.client is None:
            async with httpx.AsyncClient(**self.kwargs) as client:
                tasks = [
                    self.create_task(spider_cls, client)
                    for spider_cls in self.spiders_cls
                ]
                responses = await asyncio.gather(*tasks)
        else:
            tasks = [
                self.create_task(spider_cls, self.client)
                for spider_cls in self.spiders_cls
            ]
            responses = await asyncio.gather(*tasks)

        return self.parse(responses)
