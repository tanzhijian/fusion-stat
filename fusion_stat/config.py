from .types import base_types

MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League": base_types.ParamsDict(
        fotmob_id="47",
        fbref_id="9",
    ),
    "La Liga": base_types.ParamsDict(
        fotmob_id="87",
        fbref_id="12",
    ),
    "Bundesliga": base_types.ParamsDict(
        fotmob_id="54",
        fbref_id="20",
    ),
    "Serie A": base_types.ParamsDict(
        fotmob_id="55",
        fbref_id="11",
    ),
    "Ligue 1": base_types.ParamsDict(
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
