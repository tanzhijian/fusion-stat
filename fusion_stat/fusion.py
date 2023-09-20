# mypy: ignore-errors

import asyncio
import typing

from rapidfuzz import process

from .clients import FotMob, FBref
from .config import COMPETITIONS
from .models import (
    Competitions as CompetitionsModel,
    Competition as CompetitionModel,
)


class Competitions:
    def __init__(self) -> None:
        self.data = None

    @staticmethod
    async def _create_task(client_cls, **kwargs):
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

    async def _init_index(self) -> dict[str, typing.Any]:
        competitions = await self.get()
        data = {}

        for competition in competitions.fotmob:
            *_, index = process.extractOne(competition.name, COMPETITIONS)
            data[index] = {
                "fotmob": {
                    "id": competition.id,
                    "name": competition.name,
                }
            }

        for competition in competitions.fbref:
            *_, index = process.extractOne(competition.name, COMPETITIONS)
            data[index]["fbref"] = {
                "id": competition.id,
                "name": competition.name,
            }

        return data
