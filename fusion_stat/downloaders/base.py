import typing
from abc import ABC, abstractmethod
from types import TracebackType

import httpx

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
