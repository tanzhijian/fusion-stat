from .models.base import ParamsDict

MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League": ParamsDict(
        fotmob_id="47",
        fbref_id="9",
    ),
    "La Liga": ParamsDict(
        fotmob_id="87",
        fbref_id="12",
    ),
    "Bundesliga": ParamsDict(
        fotmob_id="54",
        fbref_id="20",
    ),
    "Serie A": ParamsDict(
        fotmob_id="55",
        fbref_id="11",
    ),
    "Ligue 1": ParamsDict(
        fotmob_id="53",
        fbref_id="13",
    ),
}

POSITIONS = {
    "goalkeepers": "GK",
    "GK": "GK",
    "defenders": "DF",
    "DF": "DF",
    "midfielders": "MF",
    "MF": "MF",
    "attackers": "FW",
    "FW": "FW",
}
