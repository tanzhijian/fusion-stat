import typing
from abc import ABC, abstractmethod
from types import TracebackType

import httpx
from httpx._types import URLTypes


U = typing.TypeVar("U", bound="Client")


class Client(ABC):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
    ) -> None:
        self.client_cls = client_cls
        self.kwargs = kwargs

    @abstractmethod
    async def get(self, url: URLTypes, **kwargs: typing.Any) -> typing.Any:
        ...

    async def __aenter__(self: U) -> U:
        self.client = self.client_cls(**self.kwargs)
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_value: typing.Optional[BaseException] = None,
        traceback: typing.Optional[TracebackType] = None,
    ) -> None:
        await self.client.aclose()

    async def _get(
        self, url: URLTypes, **kwargs: typing.Any
    ) -> httpx.Response:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response


class JSONClient(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client_cls, **kwargs)

    async def get(self, url: URLTypes, **kwargs: typing.Any) -> typing.Any:
        response = await self._get(url, **kwargs)
        return response.json()


class HTMLClient(Client):
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client_cls, **kwargs)

    async def get(self, url: URLTypes, **kwargs: typing.Any) -> str:
        response = await self._get(url, **kwargs)
        return response.text