import asyncio
import typing
from abc import ABC, abstractmethod
import httpx
from httpx._types import ProxiesTypes

from fusion_stat.clients.base import Client


T = typing.TypeVar("T")


class FusionStat(typing.Generic[T], ABC):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        self.httpx_client_cls = httpx_client_cls
        self.proxies = proxies
        self._response: T | None = None

    @property
    @abstractmethod
    def _clients_cls(self) -> list[type[Client]]:
        ...

    @property
    def response(self) -> T:
        if self._response is None:
            raise ValueError("Confirm get() has been executed")
        return self._response

    @response.setter
    def response(self, value: T) -> None:
        self._response = value

    @abstractmethod
    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        ...

    @abstractmethod
    def _parse(self, data: list[httpx.Response]) -> T:
        ...

    async def get(self) -> T:
        tasks = [
            self._create_task(client_cls) for client_cls in self._clients_cls
        ]
        data = await asyncio.gather(*tasks)

        self.response = self._parse(data)
        return self.response
