from .types import competitions_types

MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League": competitions_types.BaseCompetitionParamsDict(
        fotmob_id="47",
        fbref_id="9",
        transfermarkt_id="GB1",
    ),
    "La Liga": competitions_types.BaseCompetitionParamsDict(
        fotmob_id="87",
        fbref_id="12",
        transfermarkt_id="ES1",
    ),
    "Bundesliga": competitions_types.BaseCompetitionParamsDict(
        fotmob_id="54",
        fbref_id="20",
        transfermarkt_id="L1",
    ),
    "Serie A": competitions_types.BaseCompetitionParamsDict(
        fotmob_id="55",
        fbref_id="11",
        transfermarkt_id="IT1",
    ),
    "Ligue 1": competitions_types.BaseCompetitionParamsDict(
        fotmob_id="53",
        fbref_id="13",
        transfermarkt_id="FR1",
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
