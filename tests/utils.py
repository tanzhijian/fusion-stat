import typing
import json
from pathlib import Path

import httpx
import respx


def read_fotmob_test_data(file: str) -> typing.Any:
    with open(Path(f"tests/data/fotmob/{file}")) as f:
        data = json.load(f)
    return data


def read_fbref_test_data(file: str) -> str:
    with open(Path(f"tests/data/fbref/{file}")) as f:
        text = f.read()
    return text


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
