from . import Stat


class Match:
    def __init__(
        self,
        fotmob: Stat,
        fbref: Stat,
    ) -> None:
        self.fotmob = fotmob
        self.fbref = fbref
