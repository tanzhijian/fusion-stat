import typing
import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop() -> (
    typing.Generator[asyncio.AbstractEventLoop, typing.Any, None]
):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
