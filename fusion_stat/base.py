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

    async def get(self, request: httpx.Request) -> httpx.Response:
        response = await self.client.send(request)
        response.raise_for_status()
        return response

    @property
    @abstractmethod
    def request(self) -> httpx.Request:
        ...

    @abstractmethod
    def parse(self, response: httpx.Response) -> typing.Any:
        ...

    async def process(self) -> typing.Any:
        response = await self.get(self.request)
        return self.parse(response)


class Collector(typing.Generic[T], ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        if client is None:
            self.has_client = False
            self.client = httpx.AsyncClient(**kwargs)
        else:
            self.has_client = True
            self.client = client

    @property
    @abstractmethod
    def tasks(
        self,
    ) -> tuple[typing.Coroutine[typing.Any, typing.Any, typing.Any], ...]:
        ...

    @abstractmethod
    def parse(self, items: list[typing.Any]) -> T:
        ...

    async def gather(self) -> T:
        result = await asyncio.gather(*self.tasks)

        if not self.has_client:
            await self.client.aclose()

        return self.parse(result)
