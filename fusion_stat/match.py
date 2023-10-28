import typing

import httpx

from .base import FusionStat
from .downloaders.base import Spider
from .downloaders.fotmob import Match as FotMobMatch
from .downloaders.fbref import Match as FBrefMatch
from .utils import unpack_params
from .models import Params


class Match(FusionStat):
    def __init__(
        self,
        params: Params | dict[str, str],
        *,
        client: httpx.AsyncClient | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.params = unpack_params(params)

    @property
    def spiders_cls(self) -> tuple[type[Spider], ...]:
        return (FotMobMatch, FBrefMatch)

    async def _create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **self.params[spider_cls.module_name],
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response
