import asyncio
import typing
from abc import ABC, abstractmethod
import httpx

from fusion_stat.clients.base import Client


T = typing.TypeVar("T")


class FusionStat(typing.Generic[T], ABC):
    def __init__(
        self, client: httpx.AsyncClient | None = None, **kwargs: typing.Any
    ) -> None:
        self.client = client
        self.kwargs = kwargs
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
        self, client_cls: type[Client], client: httpx.AsyncClient
    ) -> httpx.Response:
        ...

    @abstractmethod
    def _parse(self, data: list[httpx.Response]) -> T:
        ...

    async def get(self) -> T:
        if self.client is None:
            async with httpx.AsyncClient(**self.kwargs) as client:
                tasks = [
                    self._create_task(client_cls, client)
                    for client_cls in self._clients_cls
                ]
                data = await asyncio.gather(*tasks)
        else:
            tasks = [
                self._create_task(client_cls, self.client)
                for client_cls in self._clients_cls
            ]
            data = await asyncio.gather(*tasks)

        self.response = self._parse(data)
        return self.response
