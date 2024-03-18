from fifacodes import Members

MEMBERS_SIMILARITY_SCORE = 80


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
