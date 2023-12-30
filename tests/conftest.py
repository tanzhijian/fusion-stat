import asyncio
import typing

import httpx
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop() -> (
    typing.Generator[asyncio.AbstractEventLoop, typing.Any, None]
):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client() -> typing.AsyncGenerator[httpx.AsyncClient, typing.Any]:
    async with httpx.AsyncClient() as client:
        yield client
