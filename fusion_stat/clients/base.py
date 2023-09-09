import typing
from abc import ABC, abstractmethod
from types import TracebackType

import httpx


U = typing.TypeVar("U", bound="Client")


class Client(ABC):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        self.client_cls = client_cls

    @abstractmethod
    async def get(self, url: str) -> typing.Any:
        ...

    async def __aenter__(self: U) -> U:
        self.client = self.client_cls()
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_value: typing.Optional[BaseException] = None,
        traceback: typing.Optional[TracebackType] = None,
    ) -> None:
        await self.client.aclose()

    async def _get(self, url: str) -> httpx.Response:
        response = await self.client.get(url)
        response.raise_for_status()
        return response


class JSONClient(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        super().__init__(client_cls)

    async def get(self, url: str) -> typing.Any:
        response = await self._get(url)
        return response.json()


class HTMLClient(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        super().__init__(client_cls)

    async def get(self, url: str) -> str:
        response = await self._get(url)
        return response.text
