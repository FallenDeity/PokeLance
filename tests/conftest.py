"""Shared pytest fixtures for PokeLance tests."""

from __future__ import annotations

import typing as t

import pytest
import pytest_asyncio

from pokelance import PokeLanceAsyncClient, PokeLanceSyncClient


@pytest.fixture(autouse=True)
def clear_all_caches() -> t.Generator[None, None, None]:
    _clear()
    yield
    _clear()


def _clear() -> None:
    c = PokeLanceSyncClient(cache_endpoints=False)
    c.http.cache_manager.clear()
    c.http.cache_manager.reset()
    PokeLanceAsyncClient.get_image.cache_clear()
    PokeLanceAsyncClient.get_audio.cache_clear()


@pytest_asyncio.fixture
async def client() -> t.AsyncGenerator[PokeLanceAsyncClient, None]:
    """Minimal async client list-endpoint registries are NOT pre-populated."""
    async with PokeLanceAsyncClient(cache_endpoints=False) as c:
        yield c


@pytest_asyncio.fixture
async def cached_client() -> t.AsyncGenerator[PokeLanceAsyncClient, None]:
    """Full async client all list-endpoint registries populated via wait_until_ready()."""
    async with PokeLanceAsyncClient(cache_endpoints=True) as c:
        await c.wait_until_ready()
        yield c


@pytest.fixture
def sync_client() -> t.Generator[PokeLanceSyncClient, None, None]:
    """Minimal sync client list-endpoint registries are NOT pre-populated."""
    with PokeLanceSyncClient(cache_endpoints=False) as c:
        yield c


@pytest.fixture
def sync_cached_client() -> t.Generator[PokeLanceSyncClient, None, None]:
    """Full sync client all list-endpoint registries populated via wait_until_ready()."""
    with PokeLanceSyncClient(cache_endpoints=True) as c:
        c.wait_until_ready()
        yield c
