"""
Shared pytest fixtures for PokeLance tests.

Cache isolation
---------------
BaseCache instances are attrs field defaults created once at class-definition
time and shared across every PokeLance instance in the process.

The clear_all_caches autouse fixture uses a short-lived PokeLance instance to
reach the shared Cache object and calls cache.clear(), which now cascades fully:
Cache.clear() -> Base.clear() -> BaseCache.clear() on every sub-cache.

Endpoint registries (_endpoints) are intentionally left intact so cached_client
tests don't have to re-fetch name lists on every test.

The class-level alru_cache for images and audio is also reset since it is
equally shared across all client instances.
"""
import typing as t

import pytest
import pytest_asyncio

import pokelance


@pytest.fixture(autouse=True)
def clear_all_caches() -> t.Generator[None, None, None]:
    _clear()
    yield
    _clear()


def _clear() -> None:
    # Instantiate a bare client just to reach the shared Cache singleton and
    # call the full cascade: Cache.clear() -> Base.clear() -> BaseCache.clear()
    c = pokelance.PokeLance(cache_endpoints=False)
    c.http.cache.clear()
    c.http.cache.reset()
    pokelance.PokeLance.get_image_async.cache_clear()
    pokelance.PokeLance.get_audio_async.cache_clear()


@pytest_asyncio.fixture
async def client() -> t.AsyncGenerator[pokelance.PokeLance, None]:
    """Minimal client list-endpoint registries are NOT pre-populated."""
    async with pokelance.PokeLance(cache_endpoints=False) as c:
        yield c


@pytest_asyncio.fixture
async def cached_client() -> t.AsyncGenerator[pokelance.PokeLance, None]:
    """Full client all list-endpoint registries populated via wait_until_ready()."""
    async with pokelance.PokeLance(cache_endpoints=True) as c:
        await c.wait_until_ready()
        yield c
