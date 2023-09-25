import asyncio
from abc import ABC, abstractmethod

import httpx
from httpx._types import ProxiesTypes

from fusion_stat.models import Response
from fusion_stat.clients import FotMob, FBref
from fusion_stat.clients.base import Client


class FusionStat(ABC):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        self.httpx_client_cls = httpx_client_cls
        self.proxies = proxies
        self._response: Response | None = None

    @property
    def response(self) -> Response:
        if self._response is None:
            raise ValueError("Confirm get() has been executed")
        return self._response

    @response.setter
    def response(self, value: Response) -> None:
        self._response = value

    @abstractmethod
    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        raise NotImplementedError

    async def get(self) -> Response:
        tasks = [
            self._create_task(FotMob),
            self._create_task(FBref),
        ]
        fotmob, fbref = await asyncio.gather(*tasks)
        self.response = Response(fotmob=fotmob.json(), fbref=fbref.text)
        return self.response
