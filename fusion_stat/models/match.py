from .base import StatDict


class Match:
    def __init__(
        self,
        fotmob: StatDict,
        fbref: StatDict,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
