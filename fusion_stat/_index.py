from rapidfuzz import process

from .config import COMPETITIONS
from .models import Competitions as CompetitionsModel


def get_competitions_index(
    competitions: CompetitionsModel,
) -> dict[str, dict[str, dict[str, str]]]:
    data: dict[str, dict[str, dict[str, str]]] = {
        key: {} for key in COMPETITIONS
    }

    for name, competition_list in [
        ("fotmob", competitions.fotmob),
        ("fbref", competitions.fbref),
    ]:
        for competition in competition_list:
            *_, index = process.extractOne(competition.name, COMPETITIONS)
            data[str(index)][name] = {
                "id": competition.id,
                "name": competition.name,
            }

    return data
