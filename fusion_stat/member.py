import typing

import httpx

from .base import Fusion
from .downloaders.base import Spider
from .downloaders.fotmob import Member as FotMobMember
from .downloaders.fbref import Member as FBrefMember
from .utils import unpack_params
from .models import Params, MemberFotMob, MemberFBref


class Response(typing.NamedTuple):
    fotmob: MemberFotMob
    fbref: MemberFBref


class Member(Fusion[Response]):
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
        return (FotMobMember, FBrefMember)

    async def create_task(
        self, spider_cls: type[Spider], client: httpx.AsyncClient
    ) -> typing.Any:
        spider = spider_cls(
            **self.params[spider_cls.module_name],
            client=client,
            **self.kwargs,
        )
        response = await spider.download()
        return response

    def parse(self, responses: list[typing.Any]) -> Response:
        fotmob, fbref = responses
        return Response(fotmob=fotmob, fbref=fbref)
