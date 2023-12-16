from . import FBrefShooting, Stat


class FotMob(Stat):
    country: str
    is_staff: bool
    position: str


class FBref(Stat):
    shooting: FBrefShooting


class Member:
    def __init__(
        self,
        fotmob: FotMob,
        fbref: FBref,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
