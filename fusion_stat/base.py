import asyncio
import typing
from abc import ABC, abstractmethod
import httpx

from fusion_stat.downloaders.base import Downloader


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
    def _downloaders_cls(self) -> list[type[Downloader]]:
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
        self, downloader_cls: type[Downloader], client: httpx.AsyncClient
    ) -> httpx.Response:
        ...

    @abstractmethod
    def _parse(self, data: list[httpx.Response]) -> T:
        ...

    async def get(self) -> None:
        if self.client is None:
            async with httpx.AsyncClient(**self.kwargs) as client:
                tasks = [
                    self._create_task(downloader_cls, client)
                    for downloader_cls in self._downloaders_cls
                ]
                data = await asyncio.gather(*tasks)
        else:
            tasks = [
                self._create_task(downloader_cls, self.client)
                for downloader_cls in self._downloaders_cls
            ]
            data = await asyncio.gather(*tasks)

        self.response = self._parse(data)
