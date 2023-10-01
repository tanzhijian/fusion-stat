import typing

import httpx

from .base import Downloader
from fusion_stat.models import Params
from fusion_stat.utils import unpack_params


class FBref(Downloader):
    def __init__(
        self, client: httpx.AsyncClient, **kwargs: typing.Any
    ) -> None:
        super().__init__(client, **kwargs)
        # pytest_httpx 会造成 client.base_url = "https://fbref.com/en" 类型提示错误
        # 暂时先这样写，后续解决了再设置 self.client.base_url
        self.base_url = "https://fbref.com/en"

    async def get_competitions(self) -> httpx.Response:
        path = self.base_url + "/comps/"
        response = await self.get(path)
        return response

    async def get_competition(
        self,
        params: Params | dict[str, str],
        season: str | None = None,
    ) -> httpx.Response:
        params = unpack_params(params)
        if season:
            path = "/comps" + f"/{params.fbref_id}/{season}"
            if params.fbref_path_name:
                path += f"/{season}-{params.fbref_path_name}-Stats"
        else:
            path = "/comps" + f"/{params.fbref_id}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"

        path = self.base_url + path

        response = await self.get(path)
        return response

    async def get_team(
        self,
        params: Params | dict[str, str],
        season: str | None = None,
    ) -> httpx.Response:
        params = unpack_params(params)
        if season:
            path = "/squads" + f"/{params.fbref_id}/{season}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"
        else:
            path = "/squads" + f"/{params.fbref_id}"
            if params.fbref_path_name:
                path += f"/{params.fbref_path_name}-Stats"

        path = self.base_url + path

        response = await self.get(path)
        return response

    async def get_player(
        self,
        params: Params | dict[str, str],
    ) -> httpx.Response:
        params = unpack_params(params)
        path = f"/players/{params.fbref_id}/"
        if params.fbref_path_name:
            path += params.fbref_path_name

        path = self.base_url + path

        response = await self.get(path)
        return response
