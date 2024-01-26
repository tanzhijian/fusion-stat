import json
import typing
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


def fotmob_mock(file: str) -> respx.Route:
    data = read_data("fotmob", file)
    route = respx.get(
        url=f"https://www.fotmob.com/api/{file.split('.')[0]}"
    ).mock(httpx.Response(200, json=data))
    return route


def fbref_mock(file: str) -> respx.Route:
    text = read_data("fbref", file)
    route = respx.get(
        f"https://fbref.com/en/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, text=text))
    return route


def premier_league_mock(file: str) -> respx.Route:
    data = read_data("premier_league", file)
    url = f"https://footballapi.pulselive.com/football/{file.split('.')[0]}"
    route = respx.get(url).mock(httpx.Response(200, json=data))
    return route


def transfermarkt_mock(file: str) -> respx.Route:
    data = read_data("transfermarkt", file)
    if file.split(".")[-1] == "json":
        params = {"json": data}
    else:
        params = {"text": data}
    route = respx.get(
        f"https://www.transfermarkt.com/{file.replace('_', '/').split('.')[0]}"
    ).mock(httpx.Response(200, **params))
    return route
