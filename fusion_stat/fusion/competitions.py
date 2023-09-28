import asyncio
import typing

import httpx
from httpx._types import ProxiesTypes
from pydantic import BaseModel
from rapidfuzz import process
from parsel import Selector

from fusion_stat.utils import get_element_text
from fusion_stat.clients.base import Client
from fusion_stat.clients import FotMob, FBref
from fusion_stat.config import COMPETITIONS, SCORE_CUTOFF
from fusion_stat.models import (
    Stat,
    Params,
)


class CompetitionModel(Stat):
    ...


class Response(BaseModel):
    fotmob: tuple[CompetitionModel, ...]
    fbref: tuple[CompetitionModel, ...]


class Competitions:
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

    async def get(self) -> Response:
        tasks = [
            self._create_task(FotMob),
            self._create_task(FBref),
        ]
        fotmob, fbref = await asyncio.gather(*tasks)

        fotmob_competitions = self._parse_fotmob(fotmob.json())
        fbref_competitions = self._parse_fbref(fbref.text)
        self.response = Response(
            fotmob=fotmob_competitions, fbref=fbref_competitions
        )
        return self.response

    def index(self) -> list[Params]:
        data: list[Params] = []

        for fotmob_competition in self.response.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.response.fbref,
                processor=lambda x: x.name,
            )[0]

            data.append(
                Params(
                    fotmob_id=fotmob_competition.id,
                    fbref_id=fbref_competition.id,
                    fbref_path_name=fbref_competition.name.replace(" ", "-"),
                )
            )

        return data

    def _parse_fotmob(self, json: typing.Any) -> tuple[CompetitionModel, ...]:
        competitions: list[CompetitionModel] = []
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
        return tuple(competitions)

    def _parse_fbref(self, text: str) -> tuple[CompetitionModel, ...]:
        competitions: list[CompetitionModel] = []

        selector = Selector(text)
        index = set()
        trs = selector.xpath(
            "//table[@id='comps_intl_club_cup' or @id='comps_club']/tbody/tr"
        )
        for tr in trs:
            href = get_element_text(tr.xpath("./th/a/@href")).split("/")
            id = href[3]
            if id not in index:
                index.add(id)
                gender = get_element_text(
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
        return tuple(competitions)
