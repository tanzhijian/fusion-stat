import typing

import httpx
from pydantic import BaseModel
from rapidfuzz import process
from parsel import Selector

from .base import FusionStat
from fusion_stat.utils import get_element_text
from fusion_stat.downloaders.base import Downloader
from fusion_stat.downloaders import FotMob, FBref
from fusion_stat.config import COMPETITIONS, SCORE_CUTOFF
from fusion_stat.models import Stat, Params


class CompetitionModel(Stat):
    ...


class Response(BaseModel):
    fotmob: tuple[CompetitionModel, ...]
    fbref: tuple[CompetitionModel, ...]


class Competitions(FusionStat[Response]):
    def __init__(
        self, client: httpx.AsyncClient | None = None, **kwargs: typing.Any
    ) -> None:
        super().__init__(client, **kwargs)

    @property
    def _downloaders_cls(self) -> list[type[Downloader]]:
        return [FotMob, FBref]

    async def _create_task(
        self, downloader_cls: type[Downloader], client: httpx.AsyncClient
    ) -> httpx.Response:
        downloader = downloader_cls(client=client, **self.kwargs)
        competitions = await downloader.get_competitions()
        return competitions

    def _parse(self, data: list[httpx.Response]) -> Response:
        fotmob_response, fbref_response = data
        fotmob = self._parse_fotmob(fotmob_response.json())
        fbref = self._parse_fbref(fbref_response.text)
        return Response(fotmob=fotmob, fbref=fbref)

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

    def index(self) -> list[Params]:
        params: list[Params] = []

        for fotmob_competition in self.response.fotmob:
            fbref_competition = process.extractOne(
                fotmob_competition,
                self.response.fbref,
                processor=lambda x: x.name,
            )[0]

            params.append(
                Params(
                    fotmob_id=fotmob_competition.id,
                    fbref_id=fbref_competition.id,
                    fbref_path_name=fbref_competition.name.replace(" ", "-"),
                )
            )

        return params
