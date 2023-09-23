import typing
from types import TracebackType

import httpx
from httpx._types import URLTypes


U = typing.TypeVar("U", bound="Client")


class Client:
    def __init__(
        self,
        client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        **kwargs: typing.Any,
    ) -> None:
        self.client_cls = client_cls
        self.kwargs = kwargs

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

    async def get(self, url: URLTypes, **kwargs: typing.Any) -> httpx.Response:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response
