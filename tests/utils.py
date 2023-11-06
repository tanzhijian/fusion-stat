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


def fotmob_mock(file: str) -> None:
    data = read_data("fotmob", file)
    respx.get(url=f"https://www.fotmob.com/api/{file.split('.')[0]}").mock(
        httpx.Response(200, json=data)
    )


def fbref_mock(file: str) -> None:
    text = read_data("fbref", file)
    respx.get(
        f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, text=text))
