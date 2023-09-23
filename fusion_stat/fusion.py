import typing
import asyncio

import httpx
from httpx._types import ProxiesTypes
from parsel import Selector, SelectorList
from rapidfuzz import process

from .clients.base import Client
from .clients import FotMob, FBref
from .config import COMPETITIONS, SCORE_CUTOFF
from .models import (
    Competition as CompetitionModel,
    Competitions as CompetitionsModel,
    CompetitionDetails as CompetitionDetailsModel,
    Team as TeamModel,
)


class Competitions:
    def __init__(
        self,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        self.httpx_client_cls = httpx_client_cls
        self.proxies = proxies
        self.data: CompetitionsModel | None = None

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

    async def get(self) -> CompetitionsModel:
        if not self.data:
            tasks = [
                self._create_task(FotMob),
                self._create_task(FBref),
            ]
            fotmob_response, fbref_response = await asyncio.gather(*tasks)

            fotmob = self._parse_fotmob(fotmob_response.json())
            fbref = self._parse_fbref(fbref_response.text)

            self.data = CompetitionsModel(fotmob=fotmob, fbref=fbref)
        return self.data

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
    def _parse_fbref(html: str) -> list[CompetitionModel]:
        selector = Selector(html)
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


class Competition:
    def __init__(
        self,
        id: str,
        httpx_client_cls: type[httpx.AsyncClient] = httpx.AsyncClient,
        proxies: ProxiesTypes | None = None,
    ) -> None:
        if id not in COMPETITIONS:
            raise KeyError(
                f"Please enter a valid id: {tuple(COMPETITIONS.keys())}"
            )
        self.id = id
        self.httpx_client_cls = httpx_client_cls
        self.proxies = proxies
        self.data: CompetitionDetailsModel | None = None

    async def _create_task(
        self,
        client_cls: type[Client],
    ) -> httpx.Response:
        async with client_cls(
            httpx_client_cls=self.httpx_client_cls,
            proxies=self.proxies,
        ) as client:
            competitions = await client.get_competition(self.id)
        return competitions

    async def get(self) -> CompetitionDetailsModel:
        if not self.data:
            tasks = [
                self._create_task(FotMob),
                self._create_task(FBref),
            ]
            fotmob_response, fbref_response = await asyncio.gather(*tasks)

            teams = [
                TeamModel(
                    id="asd",
                    name="asd",
                    names={"asd"},
                    shooting=12,
                )
            ]

            self.data = CompetitionDetailsModel(
                id=self.id,
                name="asd",
                type="asd",
                season="asd",
                names={"asd"},
                teams=teams,
            )

        return self.data


def _get_element_text(selector_list: SelectorList[Selector]) -> str:
    if (text := selector_list.get()) is None:
        raise ValueError("tag not found")
    return text
