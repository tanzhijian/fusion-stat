import asyncio
import typing
from abc import ABC, abstractmethod
import httpx

from fusion_stat.downloaders.base import Spider


class FusionStat(ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        self.client = client
        self.kwargs = kwargs
        self._responses: tuple[typing.Any, ...] | None = None

    @property
    @abstractmethod
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        ...

    @property
    def responses(self) -> tuple[typing.Any, ...]:
        if self._responses is None:
            raise ValueError("Confirm get() has been executed")
        return self._responses

    @responses.setter
    def responses(self, value: tuple[typing.Any, ...]) -> None:
        self._responses = value

    @abstractmethod
    async def _create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        ...

    async def get(self) -> None:
        if self.client is None:
            async with httpx.AsyncClient(**self.kwargs) as client:
                tasks = [
                    self._create_task(spider_cls, client)
                    for spider_cls in self.spiders_cls
                ]
                responses = await asyncio.gather(*tasks)
        else:
            tasks = [
                self._create_task(spider_cls, self.client)
                for spider_cls in self.spiders_cls
            ]
            responses = await asyncio.gather(*tasks)

        self.responses = tuple(responses)
