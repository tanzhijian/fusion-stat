from abc import ABC

import httpx
from httpx._types import ProxiesTypes


class Response:
    ...


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
