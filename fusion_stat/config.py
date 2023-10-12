from .models import Params


COMPETITIONS_SIMILARITY_SCORE = 90
MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League",
    "LaLiga",
    "Bundesliga",
    "Serie A",
    "Ligue 1",
    "Champions League",
}

COMPETITIONS_INDEX = (
    Params(fotmob_id="47", fbref_id="9", fbref_path_name="Premier-League"),
    Params(fotmob_id="42", fbref_id="8", fbref_path_name="Champions-League"),
    Params(fotmob_id="87", fbref_id="12", fbref_path_name="La-Liga"),
    Params(fotmob_id="54", fbref_id="20", fbref_path_name="Bundesliga"),
    Params(fotmob_id="55", fbref_id="11", fbref_path_name="Serie-A"),
    Params(fotmob_id="53", fbref_id="13", fbref_path_name="Ligue-1"),
)

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
