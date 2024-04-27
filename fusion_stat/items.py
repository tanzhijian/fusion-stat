from abc import abstractmethod

from pydantic import BaseModel, Field

from .refactored_models import Base, Competition, Match, Player, Staff, Team


class BaseItem(BaseModel):
    id: str = Field(exclude=True)
    name: str = Field(exclude=True)

    @abstractmethod
    def convert_model(self) -> Base:
        ...


class BaseCompetitionItem(BaseItem):
    country_code: str = Field(exclude=True)
    season: int = Field(exclude=True)
    teams: list["BaseTeamItem"] | None = Field(default=None, exclude=True)
    matches: list["BaseMatchItem"] | None = Field(default=None, exclude=True)

    def convert_model(self) -> Competition:
        optional = {}
        if self.teams:
            optional["teams"] = [item.convert_model() for item in self.teams]
        if self.matches:
            optional["matches"] = [
                item.convert_model() for item in self.matches
            ]

        return Competition(
            id=self.id,
            name=self.name,
            items=self.model_dump(),
            country_code=self.country_code,
            season=self.season,
            **optional,
        )


class BaseTeamItem(BaseItem):
    country_code: str = Field(exclude=True)
    staffs: list["BaseStaffItem"] | None = Field(default=None, exclude=True)
    players: list["BasePlayerItem"] | None = Field(default=None, exclude=True)

    def convert_model(self) -> Team:
        optional = {}
        if self.staffs:
            optional["staffs"] = [item.convert_model() for item in self.staffs]
        if self.players:
            optional["matches"] = [
                item.convert_model() for item in self.players
            ]

        return Team(
            id=self.id,
            name=self.name,
            items=self.model_dump(),
            country_code=self.country_code,
            **optional,
        )


class BaseStaffItem(BaseItem):
    country_code: str = Field(exclude=True)
    position: str = Field(exclude=True)

    def convert_model(self) -> Staff:
        return Staff(
            id=self.id,
            name=self.name,
            items=self.model_dump(),
            country_code=self.country_code,
            position=self.position,
        )


class BasePlayerItem(BaseItem):
    country_code: str = Field(exclude=True)
    position: str = Field(exclude=True)

    def convert_model(self) -> Player:
        return Player(
            id=self.id,
            name=self.name,
            items=self.model_dump(),
            country_code=self.country_code,
            position=self.position,
        )


class BaseMatchItem(BaseItem):
    date: str = Field(exclude=True)
    competition: BaseCompetitionItem
    home: BaseTeamItem
    away: BaseTeamItem

    def convert_model(self) -> Match:
        return Match(
            id=self.id,
            name=self.name,
            items=self.model_dump(),
            date=self.date,
            competition=self.competition.convert_model(),
            home=self.home.convert_model(),
            away=self.away.convert_model(),
        )
