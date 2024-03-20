from fifacodes import Members

COMPETITIONS_SCORE_CUTOFF = 90
MEMBERS_SCORE_CUFOFF = 80


class CompetitionsConfig:
    data = (
        ("ENG", "Premier League"),
        ("ESP", "La Liga"),
        ("GER", "Bundesliga"),
        ("ITA", "Serie A"),
        ("FRA", "Ligue 1"),
    )

    countries = {com[0] for com in data}
    names = {com[1] for com in data}


POSITIONS = {
    "goalkeepers": "GK",
    "Keeper": "GK",
    "Goalkeeper": "GK",
    "GK": "GK",
    "defenders": "DF",
    "Defender": "DF",
    "Centre-Back": "DF",
    "Left-Back": "DF",
    "Right-Back": "DF",
    "DF": "DF",
    "midfielders": "MF",
    "Midfielder": "MF",
    "Defensive Midfield": "MF",
    "Central Midfield": "MF",
    "Right Midfield": "MF",
    "Left Midfield": "MF",
    "Attacking Midfield": "MF",
    "MF": "MF",
    "attackers": "FW",
    "Attacker": "FW",
    "Left Winger": "FW",
    "Right Winger": "FW",
    "Centre-Forward": "FW",
    "FW": "FW",
}

fifa_members = Members()
