import typing
from types import TracebackType

import httpx
from httpx._types import URLTypes

from fusion_stat.models import Params


U = typing.TypeVar("U", bound="Downloader")


class Downloader:
    def __init__(
        self,
        client: httpx.AsyncClient,
        **kwargs: typing.Any,
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

    async def get(self, url: URLTypes, **kwargs: typing.Any) -> httpx.Response:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    async def get_competitions(self) -> httpx.Response:
        raise NotImplementedError

    async def get_competition(
        self, params: Params | dict[str, str]
    ) -> httpx.Response:
        raise NotImplementedError

    async def get_team(self, params: Params) -> httpx.Response:
        raise NotImplementedError

    async def get_player(self, params: Params) -> httpx.Response:
        raise NotImplementedError