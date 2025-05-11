import pytest
import sys
import asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"  # or "trio" if you prefer


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
