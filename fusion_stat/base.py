import typing
from abc import ABC, abstractmethod
from types import TracebackType

import httpx

U = typing.TypeVar("U")


class Downloader(ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if client is None:
            self.client = httpx.AsyncClient()
        else:
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


class Spider(Downloader, ABC):
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
