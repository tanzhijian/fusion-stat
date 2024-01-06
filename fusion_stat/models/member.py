from .base import FBrefShootingDict, StatDict


class FotMobDict(StatDict):
    country: str
    is_staff: bool
    position: str


class FBrefDict(StatDict):
    shooting: FBrefShootingDict


class Member:
    def __init__(
        self,
        fotmob: FotMobDict,
        fbref: FBrefDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
