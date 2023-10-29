import asyncio
import typing
from abc import ABC, abstractmethod
import httpx

from fusion_stat.downloaders.base import Spider


T = typing.TypeVar("T")


class Fusion(typing.Generic[T], ABC):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        self.client = client
        self.kwargs = kwargs

    @property
    @abstractmethod
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        ...

    @abstractmethod
    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        ...

    @abstractmethod
    def parse(self, responses: list[typing.Any]) -> T:
        ...

    async def get(self) -> T:
        if self.client is None:
            async with httpx.AsyncClient(**self.kwargs) as client:
                tasks = [
                    self.create_task(spider_cls, client)
                    for spider_cls in self.spiders_cls
                ]
                responses = await asyncio.gather(*tasks)
        else:
            tasks = [
                self.create_task(spider_cls, self.client)
                for spider_cls in self.spiders_cls
            ]
            responses = await asyncio.gather(*tasks)

        return self.parse(responses)
