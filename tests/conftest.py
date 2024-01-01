import typing

import httpx
import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> typing.Literal["asyncio"]:
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> typing.AsyncGenerator[httpx.AsyncClient, typing.Any]:
    async with httpx.AsyncClient() as client:
        yield client
