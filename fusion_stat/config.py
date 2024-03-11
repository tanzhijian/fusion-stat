from fifacodes import Members

MEMBERS_SIMILARITY_SCORE = 80

COMPETITIONS = {
    "Premier League": {
        "fotmob_id": "47",
        "fbref_id": "9",
        "transfermarkt_id": "GB1",
    },
    "La Liga": {
        "fotmob_id": "87",
        "fbref_id": "12",
        "transfermarkt_id": "ES1",
    },
    "Bundesliga": {
        "fotmob_id": "54",
        "fbref_id": "20",
        "transfermarkt_id": "L1",
    },
    "Serie A": {
        "fotmob_id": "55",
        "fbref_id": "11",
        "transfermarkt_id": "IT1",
    },
    "Ligue 1": {
        "fotmob_id": "53",
        "fbref_id": "13",
        "transfermarkt_id": "FR1",
    },
}

POSITIONS = {
    "goalkeepers": "GK",
    "Goalkeeper": "GK",
    "GK": "GK",
    "defenders": "DF",
    "Centre-Back": "DF",
    "Left-Back": "DF",
    "Right-Back": "DF",
    "DF": "DF",
    "midfielders": "MF",
    "Defensive Midfield": "MF",
    "Central Midfield": "MF",
    "Right Midfield": "MF",
    "Left Midfield": "MF",
    "Attacking Midfield": "MF",
    "MF": "MF",
    "attackers": "FW",
    "Left Winger": "FW",
    "Right Winger": "FW",
    "Centre-Forward": "FW",
    "FW": "FW",
}

fifa_members = Members()
