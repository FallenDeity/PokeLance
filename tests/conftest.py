import typing as t

import pytest_asyncio

import pokelance


@pytest_asyncio.fixture
async def client() -> t.AsyncGenerator[pokelance.PokeLance, None]:
    async with pokelance.PokeLance(cache_endpoints=False) as client:
        yield client


@pytest_asyncio.fixture
async def cached_client() -> t.AsyncGenerator[pokelance.PokeLance, None]:
    async with pokelance.PokeLance(cache_endpoints=True) as client:
        yield client
