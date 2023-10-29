import typing

import asyncio

import pytest
import pytest_asyncio
import httpx


@pytest.fixture(scope="module")
def event_loop() -> (
    typing.Generator[asyncio.AbstractEventLoop, typing.Any, None]
):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def client() -> typing.AsyncGenerator[httpx.AsyncClient, typing.Any]:
    async with httpx.AsyncClient() as client:
        yield client
