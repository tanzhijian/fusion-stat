import typing
import json
from pathlib import Path

import httpx
import respx


def read_data(test_name: str, file: str) -> typing.Any:
    with open(Path(f"tests/data/{test_name}/{file}")) as f:
        if file.split(".")[-1] == "json":
            data = json.load(f)
        else:
            data = f.read()
    return data


def read_fotmob_test_data(file: str) -> typing.Any:
    data = read_data("fotmob", file)
    return data


def read_fbref_test_data(file: str) -> str:
    text: str = read_data("fbref", file)
    return text


def read_wikipedia_test_data(file: str) -> typing.Any:
    data = read_data("wikipedia", file)
    return data


def read_premierleague_test_data(file: str) -> typing.Any:
    data = read_data("premierleague", file)
    return data


def read_laliga_test_data(file: str) -> typing.Any:
    data = read_data("laliga", file)
    return data


def read_bundesliga_test_data(file: str) -> typing.Any:
    data = read_data("bundesliga", file)
    return data


def read_serie_a_test_data(file: str) -> typing.Any:
    data = read_data("serie_a", file)
    return data


def read_ligue_1_test_data(file: str) -> typing.Any:
    data = read_data("ligue_1", file)
    return data


def fotmob_mock(file: str) -> None:
    data = read_fotmob_test_data(file)
    respx.get(url=f"https://www.fotmob.com/api/{file.split('.')[0]}").mock(
        httpx.Response(200, json=data)
    )


def fbref_mock(file: str) -> None:
    text = read_fbref_test_data(file)
    respx.get(
        f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, text=text))
