import asyncio
import typing
import json
from pathlib import Path

from rapidfuzz import process

from .clients import FotMob, FBref
from .clients.base import Client
from .config import COMPETITIONS
from .models import (
    Competitions as CompetitionsModel,
    Competition as CompetitionModel,
    CompetitionDetails,
    Team as TeamModel,
)


class Competitions:
    def __init__(self) -> None:
        self.data: CompetitionsModel | None = None

    @staticmethod
    async def _create_task(
        client_cls: type[Client],
        **kwargs: typing.Any,
    ) -> list[CompetitionModel]:
        async with client_cls(**kwargs) as client:
            competitions = await client.get_competitions()
        return competitions

    async def get(self) -> CompetitionsModel:
        if not self.data:
            tasks = [
                self._create_task(FotMob),
                self._create_task(FBref),
            ]
            fotmob, fbref = await asyncio.gather(*tasks)

            fotmob_competitions = [
                CompetitionModel(id=competition.id, name=competition.name)
                for competition in fotmob
            ]
            fbref_competitions = [
                CompetitionModel(id=competition.id, name=competition.name)
                for competition in fbref
            ]
            self.data = CompetitionsModel(
                fotmob=fotmob_competitions,
                fbref=fbref_competitions,
            )
        return self.data

    @staticmethod
    def _parse_index(
        competitions: CompetitionsModel,
    ) -> dict[str, dict[str, dict[str, str]]]:
        data: dict[str, dict[str, dict[str, str]]] = {
            key: {} for key in COMPETITIONS
        }

        for name, competition_list in [
            ("fotmob", competitions.fotmob),
            ("fbref", competitions.fbref),
        ]:
            for competition in competition_list:
                *_, index = process.extractOne(competition.name, COMPETITIONS)
                data[str(index)][name] = {
                    "id": competition.id,
                    "name": competition.name,
                }

        return data

    def _export_index(self, competitions: CompetitionsModel) -> None:
        data = self._parse_index(competitions)
        with open(
            Path("fusion_stat/static/competitions_index.json"), "w"
        ) as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))


class Competition:
    def __init__(self, id: str) -> None:
        if id not in COMPETITIONS:
            raise KeyError(
                f"Please enter a valid id: {tuple(COMPETITIONS.keys())}"
            )
        self.id = id
        self.data: CompetitionDetails | None = None

    async def _create_task(
        self, client_cls: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        async with client_cls(**kwargs) as client:
            competition = await client.get_competition(self.id)
        return competition

    async def get(self) -> CompetitionDetails:
        if not self.data:
            tasks = [
                self._create_task(FotMob),
                self._create_task(FBref),
            ]
            fotmob, fbref = await asyncio.gather(*tasks)

            teams = [
                TeamModel(
                    id="asd",
                    name="asd",
                    names={"asd"},
                    shooting=12,
                )
            ]

            self.data = CompetitionDetails(
                id=self.id,
                name=fotmob.name,
                type=fotmob.type,
                season=fotmob.season,
                names=fotmob.names | {fbref.name},
                teams=teams,
            )

        return self.data
