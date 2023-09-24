import typing
import json
from pathlib import Path


def read_json(path: Path) -> typing.Any:
    with open(path) as f:
        return json.load(f)


SCORE_CUTOFF = 90

COMPETITIONS = {
    "PL": "Premier League",
    "LL": "LaLiga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
    "CL": "Champions League",
}


COMPETITIONS_INDEX = read_json(
    Path(
        Path(__file__).resolve().parent,
        "static/competitions_index.json",
    )
)
