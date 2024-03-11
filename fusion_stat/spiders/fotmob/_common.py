BASE_URL = "https://www.fotmob.com/api"


def parse_score(score_str: str | None) -> tuple[int | None, int | None]:
    """
    score_str: '3 - 2' or None
    """
    home_score, away_score = (
        [int(score) for score in score_str.split(" - ")]
        if score_str is not None
        else (None, None)
    )
    return home_score, away_score
