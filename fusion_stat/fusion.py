import typing
import asyncio
from abc import ABC, abstractmethod

import httpx
from httpx._types import ProxiesTypes
from parsel import Selector, SelectorList
from rapidfuzz import process

from .clients.base import Client
from .clients import FotMob, FBref
from .config import COMPETITIONS, SCORE_CUTOFF
from .models import Response, CompetitionModel


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


class Competitions(FusionStat):
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(httpx_client_cls, proxies)

    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        async with client_cls(
            httpx_client_cls=self.httpx_client_cls,
            proxies=self.proxies,
        ) as client:
            competitions = await client.get_competitions()
        return competitions

    def index(self) -> dict[str, dict[str, dict[str, str]]]:
        fotmob = self._parse_fotmob(self.response.fotmob)
        fbref = self._parse_fbref(self.response.fbref)

        data: dict[str, dict[str, dict[str, str]]] = {
            key: {} for key in COMPETITIONS
        }

        for name, competition_list in [
            ("fotmob", fotmob),
            ("fbref", fbref),
        ]:
            for competition in competition_list:
                *_, index = process.extractOne(competition.name, COMPETITIONS)
                data[str(index)][name] = {
                    "id": competition.id,
                    "name": competition.name,
                }

        return data

    @staticmethod
    def _parse_fotmob(json: typing.Any) -> list[CompetitionModel]:
        competitions = []
        selection = json["popular"]
        for competition in selection:
            if process.extractOne(
                competition["name"], COMPETITIONS, score_cutoff=SCORE_CUTOFF
            ):
                competitions.append(
                    CompetitionModel(
                        id=str(competition["id"]),
                        name=competition["name"],
                    )
                )
        return competitions

    @staticmethod
    def _parse_fbref(selector: Selector) -> list[CompetitionModel]:
        competitions = []
        index = set()
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href = _get_element_text(tr.xpath("./th/a/@href")).split("/")
            id = href[3]
            if id not in index:
                index.add(id)
                gender = _get_element_text(
                    tr.xpath("./td[@data-stat='gender']/text()")
                )
                name = " ".join(href[-1].split("-")[:-1])
                if (
                    process.extractOne(
                        name, COMPETITIONS, score_cutoff=SCORE_CUTOFF
                    )
                    and gender == "M"
                ):
                    competitions.append(
                        CompetitionModel(
                            id=id,
                            name=name,
                        )
                    )
        return competitions


class Competition(FusionStat):
    def __init__(
        self,
        id: str,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        super().__init__(httpx_client_cls, proxies)
        if id not in COMPETITIONS:
            raise KeyError(
                f"Please enter a valid id: {tuple(COMPETITIONS.keys())}"
            )
        self.id = id

    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        async with client_cls(
            httpx_client_cls=self.httpx_client_cls,
            proxies=self.proxies,
        ) as client:
            competition = await client.get_competition(self.id)
        return competition


def _get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text
