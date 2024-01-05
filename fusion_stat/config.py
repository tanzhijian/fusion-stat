from .models import CompetitionParams

COMPETITIONS_SIMILARITY_SCORE = 90
MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League": CompetitionParams(
        fotmob_id="47",
        fbref_id="9",
        fbref_path_name="Premier-League",
        official_name="Premier League",
    ),
    "La Liga": CompetitionParams(
        fotmob_id="87",
        fbref_id="12",
        fbref_path_name="La-Liga",
        official_name="La Liga",
    ),
    "Bundesliga": CompetitionParams(
        fotmob_id="54",
        fbref_id="20",
        fbref_path_name="Bundesliga",
        official_name="Bundesliga",
    ),
    "Serie A": CompetitionParams(
        fotmob_id="55",
        fbref_id="11",
        fbref_path_name="Serie-A",
        official_name="Serie A",
    ),
    "Ligue 1": CompetitionParams(
        fotmob_id="53",
        fbref_id="13",
        fbref_path_name="Ligue-1",
        official_name="Ligue 1",
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
