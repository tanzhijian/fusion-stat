import typing

import httpx

from .base import Fusion, Spider
from .spiders.fotmob import Match as FotMobMatch
from .spiders.fbref import Match as FBrefMatch
from .utils import unpack_params
from .models import Params, Stat


class Response:
    def __init__(
        self,
        fotmob: Stat,
        fbref: Stat,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref


class Match(Fusion[Response]):
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

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **self.params[spider_cls.__module__.split(".")[-1]],
            client=client,
        )
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
