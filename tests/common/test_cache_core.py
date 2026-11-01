"""
Unit-level tests for BaseCache mechanics.

Isolation
---------
All data caches are cleared before each test by the `clear_all_caches` autouse
fixture in conftest.py. The endpoint registries are preserved so cached_client
tests don't need to re-populate them.

Coverage
--------
- max_size attribute and set_size()
- LRU eviction: oldest entry dropped when capacity exceeded
- LRU re-access refreshes MRU order
- Per-category size override
- client back-reference
- cache.get() alias resolution (id→name and name→id)
- __len__, clear()
- image and audio alru_cache: contains, cache_clear, set_size
"""

import asyncio
import math
import threading
import typing as t
from unittest.mock import AsyncMock, Mock

import pytest

import pokelance
from pokelance.cache import AsyncCache, SyncCache
from pokelance.endpoints import Endpoint, Route
from pokelance.models import BaseModel, LocationAreaEncounter
from pokelance.utils import alru_cache

# ---------------------------------------------------------------------------
# Size / attributes
# ---------------------------------------------------------------------------


def test_cache_default_max_size(client: pokelance.PokeLanceAsyncClient) -> None:
    assert client.http.cache_manager.max_size == 100


def test_cache_set_size_global(client: pokelance.PokeLanceAsyncClient) -> None:
    client.http.cache_manager.set_size(255)
    assert client.http.cache_manager.max_size == 255
    assert client.http.cache_manager.pokemon.pokemon._max_size == 255  # pyright: ignore[reportPrivateUsage]


def test_cache_set_size_per_category(client: pokelance.PokeLanceAsyncClient) -> None:
    client.http.cache_manager.pokemon.pokemon.set_size(42)
    assert client.http.cache_manager.pokemon.pokemon._max_size == 42  # pyright: ignore[reportPrivateUsage]


def test_cache_client_backref(client: pokelance.PokeLanceAsyncClient) -> None:
    assert client.http.cache_manager.client is client


@pytest.mark.parametrize("size", [0, -1])
def test_invalid_cache_capacities_are_rejected(size: int) -> None:
    for client_type in (pokelance.PokeLanceAsyncClient, pokelance.PokeLanceSyncClient):
        for option in ("cache_size", "image_cache_size", "audio_cache_size"):
            kwargs: dict[str, t.Any] = {option: size}
            with pytest.raises(ValueError, match="greater than 0"):
                client_type(setup_logging=False, **kwargs)
    for cache_type in (AsyncCache, SyncCache):
        with pytest.raises(ValueError, match="greater than 0"):
            cache_type(max_size=size)


@pytest.mark.parametrize("size", [0, -1])
def test_invalid_cache_resize_preserves_capacity(client: pokelance.PokeLanceAsyncClient, size: int) -> None:
    manager = client.http.cache_manager
    for resize in (manager.set_size, manager.pokemon.set_size, manager.pokemon.pokemon.set_size):
        with pytest.raises(ValueError, match="greater than 0"):
            resize(size)
    assert manager.max_size == 100
    assert manager.pokemon.max_size == 100
    assert manager.pokemon.pokemon._max_size == 100  # pyright: ignore[reportPrivateUsage]
    for cache in (client.get_image, client.get_audio):
        previous = cache.cache_info().maxsize
        with pytest.raises(ValueError, match="greater than 0"):
            cache.set_size(size)
        assert cache.cache_info().maxsize == previous
    with pytest.raises(ValueError, match="greater than 0"):
        alru_cache(maxsize=size)(client.http.load_image)
    assert alru_cache(maxsize=None)(client.http.load_image).cache_info().maxsize is None


# ---------------------------------------------------------------------------
# LRU eviction
# ---------------------------------------------------------------------------


def test_cache_lru_order_eviction_and_clear() -> None:
    cache = SyncCache(max_size=3)
    routes = [Endpoint.get_pokemon(i) for i in range(1, 5)]
    for route in routes[:3]:
        cache[route] = BaseModel()
    assert list(cache) == routes[:3]
    assert len(cache) == 3

    cache[routes[0]]
    cache[routes[3]] = BaseModel()
    assert list(cache) == [routes[2], routes[0], routes[3]]
    assert cache.get(routes[1]) is None
    assert cache.stats.evictions == 1

    cache.clear()
    assert len(cache) == 0


@pytest.mark.parametrize("cache_type", [AsyncCache, SyncCache])
@pytest.mark.parametrize("id_keys", [False, True])
def test_registry_indexes_reset_and_reload(
    cache_type: type[AsyncCache[t.Any, t.Any]] | type[SyncCache[t.Any, t.Any]], id_keys: bool
) -> None:
    cache = cache_type(endpoint_key_is_id=id_keys)
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    key = "1" if id_keys else "bulbasaur"
    assert set(cache.endpoints) == {key}
    assert cache.endpoints[key].id == 1
    assert cache.endpoints[key].url == "https://pokeapi.co/api/v2/pokemon/1/"
    assert cache._endpoints_by_id == {"1": key}
    assert cache.identifiers == {key, "1"}
    assert cache.is_ready and cache._ready.is_set()

    cache.reset_endpoints()
    assert not cache.is_ready and not cache._ready.is_set()
    assert cache.endpoints == {} and cache._endpoints_by_id == {}
    assert cache.identifiers == set()

    cache.load_documents([{"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"}])
    new_key = "2" if id_keys else "ivysaur"
    assert set(cache.endpoints) == {new_key}
    assert cache._endpoints_by_id == {"2": new_key}
    assert cache.identifiers == {new_key, "2"}
    assert cache.is_ready and cache._ready.is_set()


@pytest.mark.parametrize("cache_type", [AsyncCache, SyncCache])
def test_cache_shrink_immediately_evicts_lru_entries(
    cache_type: type[AsyncCache[t.Any, t.Any]] | type[SyncCache[t.Any, t.Any]],
) -> None:
    cache = cache_type(max_size=4)
    routes = [Endpoint.get_pokemon(i) for i in range(1, 5)]
    for route in routes:
        cache[route] = BaseModel()
    cache.get(routes[0])
    cache.set_size(2)
    assert list(cache) == [routes[3], routes[0]]
    assert cache.stats.evictions == 2
    cache.set_size(5)
    assert len(cache) == 2 and cache.stats.evictions == 2


@pytest.mark.asyncio
async def test_async_media_cache_shrink_evicts_lru_entries() -> None:
    @alru_cache(maxsize=4, ttl=60)
    async def download(value: int) -> bytes:
        return await asyncio.sleep(0, result=str(value).encode())

    for i in range(4):
        await download(i)
    await download(0)
    download.set_size(2)
    assert download.cache_info().currsize == 2
    assert download.__contains__(0) and download.__contains__(3)
    assert not download.__contains__(1) and not download.__contains__(2)
    await download.cache_close()


# ---------------------------------------------------------------------------
# Alias resolution in cache.get()
# ---------------------------------------------------------------------------


def test_sync_registry_reindex_preserves_concurrent_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = SyncCache()
    route = Endpoint.get_pokemon("pikachu")
    stale, fresh = BaseModel(), BaseModel()
    cache[route] = stale
    migrating, release, writing, finished = (threading.Event() for _ in range(4))
    canonicalize = cache._canonicalize_key

    def observed_canonicalize(key: Route) -> Route:
        if threading.current_thread().name == "registry-loader":
            migrating.set()
            assert release.wait(2)
        return canonicalize(key)

    def refresh() -> None:
        writing.set()
        cache[route] = fresh
        finished.set()

    monkeypatch.setattr(cache, "_canonicalize_key", observed_canonicalize)
    loader = threading.Thread(
        target=cache.load_documents,
        args=([{"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon/25/"}],),
        name="registry-loader",
    )
    writer = threading.Thread(target=refresh)
    loader.start()
    try:
        assert migrating.wait(1)
        writer.start()
        assert writing.wait(1)
        finished.wait(0.05)
    finally:
        release.set()
        loader.join(2)
        if writer.ident is not None:
            writer.join(2)
    assert not loader.is_alive() and not writer.is_alive()
    assert cache.get(Endpoint.get_pokemon(25)) is fresh


@pytest.mark.parametrize("cache_type", [AsyncCache, SyncCache])
@pytest.mark.parametrize("suffix", ["", "/encounters"])
@pytest.mark.parametrize("stored", ["1", "bulbasaur"])
def test_cache_aliases_preserve_subresource_and_lru(
    cache_type: type[AsyncCache[t.Any, t.Any]] | type[SyncCache[t.Any, t.Any]], suffix: str, stored: str
) -> None:
    cache = cache_type(url_suffix=suffix)
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    route = Route(endpoint=f"/pokemon/{stored}{suffix}")
    other = Route(endpoint=f"/pokemon/2{suffix}")
    value = [LocationAreaEncounter()] if suffix else BaseModel()
    cache[route] = value
    cache[other] = BaseModel()
    alias = "bulbasaur" if stored == "1" else "1"
    assert cache.get(Route(endpoint=f"/pokemon/{alias}{suffix}")) is value
    canonical_route = Route(endpoint=f"/pokemon/1{suffix}")
    assert list(cache)[-1] == canonical_route
    assert cache.stats.hits == 1 and cache.stats.misses == 0

    replacement = [LocationAreaEncounter()] if suffix else BaseModel()
    cache[Route(endpoint=f"/pokemon/{alias}{suffix}")] = replacement
    assert len(cache) == 2
    assert cache.get(route) is replacement
    assert cache.get(Route(endpoint=f"/pokemon/1{suffix}")) is replacement


@pytest.mark.parametrize("cache_type", [AsyncCache, SyncCache])
def test_cache_alias_entries_are_merged_when_registry_loads(
    cache_type: type[AsyncCache[t.Any, t.Any]] | type[SyncCache[t.Any, t.Any]],
) -> None:
    cache = cache_type()
    stale = BaseModel()
    fresh = BaseModel()
    cache[Route(endpoint="/pokemon/bulbasaur")] = stale
    cache[Route(endpoint="/pokemon/1")] = fresh

    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])

    assert list(cache) == [Route(endpoint="/pokemon/1")]
    assert cache.get(Route(endpoint="/pokemon/bulbasaur")) is fresh


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_empty_encounters_are_cache_hits(monkeypatch: pytest.MonkeyPatch, is_async: bool) -> None:
    client = (
        pokelance.PokeLanceAsyncClient(cache_endpoints=False, setup_logging=False)
        if is_async
        else pokelance.PokeLanceSyncClient(cache_endpoints=False, setup_logging=False)
    )
    request = AsyncMock(return_value=[]) if is_async else Mock(return_value=[])
    monkeypatch.setattr(client.http, "request", request)
    cache = client.pokemon.cache_group.location_area_encounter
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    if isinstance(client, pokelance.PokeLanceAsyncClient):
        first: list[LocationAreaEncounter] = await client.getch_data("pokemon", "location-area-encounter", 1)
        second: list[LocationAreaEncounter] = await client.getch_data("pokemon", "location-area-encounter", "bulbasaur")
        await client.pokemon.cache_group.location_area_encounter.load_all()
        await client.pokemon.cache_group.location_area_encounter.load_all_batch(batch_size=1)
        await client.close()
    else:
        first = client.getch_data("pokemon", "location-area-encounter", 1)
        second = client.getch_data("pokemon", "location-area-encounter", "bulbasaur")
        client.pokemon.cache_group.location_area_encounter.load_all()
        client.pokemon.cache_group.location_area_encounter.load_all_batch(batch_size=1)
        client.close()
    assert first == [] and second is first
    request.assert_called_once()


@pytest.mark.asyncio
async def test_cache_get_by_id_after_name_fetch(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """Fetch by name → retrieve by numeric id via alias lookup."""
    await cached_client.pokemon.fetch_pokemon("bulbasaur")
    route_by_id = Endpoint.get_pokemon(1)
    result = cached_client.http.cache_manager.pokemon.pokemon.get(route_by_id)
    assert result is not None, "Should resolve bulbasaur via its numeric id alias."
    assert result.name == "bulbasaur"


# ---------------------------------------------------------------------------
# alru_cache for images and audio
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_image_cache_contains(client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    assert url is not None, "Pokemon sprite URL should not be None."
    await client.get_image(url)
    assert client.get_image.__contains__(client, url)


@pytest.mark.asyncio
async def test_image_cache_clear(client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    assert url is not None, "Pokemon sprite URL should not be None."
    await client.get_image(url)
    client.get_image.cache_clear()
    assert not client.get_image.__contains__(client, url)


def test_image_cache_set_size(client: pokelance.PokeLanceAsyncClient) -> None:
    client.get_image.set_size(10)
    assert client.get_image.cache_info().maxsize == 10


@pytest.mark.asyncio
async def test_audio_cache_contains(client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    assert url is not None, "Pokemon cry URL should not be None."
    await client.get_audio(url)
    assert client.get_audio.__contains__(client, url)


@pytest.mark.asyncio
async def test_audio_cache_clear(client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    assert url is not None, "Pokemon cry URL should not be None."
    await client.get_audio(url)
    client.get_audio.cache_clear()
    assert not client.get_audio.__contains__(client, url)


def test_audio_cache_set_size(client: pokelance.PokeLanceAsyncClient) -> None:
    client.get_audio.set_size(10)
    assert client.get_audio.cache_info().maxsize == 10


@pytest.mark.asyncio
async def test_cancelled_async_cache_retries_without_coalescing_callers() -> None:
    calls = 0
    started, release = asyncio.Event(), asyncio.Event()

    @alru_cache()
    async def download(url: str) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise asyncio.CancelledError
        started.set()
        await release.wait()
        return b"image"

    with pytest.raises(asyncio.CancelledError):
        await download("url")
    first = asyncio.create_task(download("url"))
    await started.wait()
    second = asyncio.create_task(download("url"))
    await asyncio.sleep(0)
    first.cancel()
    with pytest.raises(asyncio.CancelledError):
        await first
    release.set()
    assert await second == b"image"
    assert calls == 3
    assert await download("url") == b"image"
    assert calls == 3
    await download.cache_close()


@pytest.mark.asyncio
async def test_async_cache_clear_preserves_replacement_and_tracks_cleanup() -> None:
    calls = 0
    started, cancelled, cleanup = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @alru_cache(ttl=60)
    async def download(url: str) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await cleanup.wait()
                raise
        return b"fresh"

    first = asyncio.create_task(download("url"))
    await started.wait()
    download.cache_clear()
    assert download.cache_parameters()["tasks"] == 1
    await cancelled.wait()
    assert await download("url") == b"fresh"
    cleanup.set()
    with pytest.raises(asyncio.CancelledError):
        await first
    assert await download("url") == b"fresh"
    assert calls == 2
    assert download.cache_parameters()["tasks"] == 0
    await download.cache_close()


@pytest.mark.asyncio
async def test_async_cache_close_drains_work_cancelled_by_clear() -> None:
    started, cancelled, cleanup = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @alru_cache()
    async def download() -> bytes:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
            await cleanup.wait()
        return b"image"

    caller = asyncio.create_task(download())
    await started.wait()
    download.cache_clear()
    await cancelled.wait()
    closer = asyncio.create_task(download.cache_close())
    await asyncio.sleep(0)
    assert not closer.done(), "cache_close() must wait for cancellation cleanup"
    cleanup.set()
    await closer
    with pytest.raises(asyncio.CancelledError):
        await caller
    assert download.cache_parameters()["tasks"] == 0


@pytest.mark.asyncio
async def test_cache_statistics(client: pokelance.PokeLanceAsyncClient) -> None:
    poke_cache = client.http.cache_manager.pokemon.pokemon
    poke_cache.stats.reset()
    poke_cache.set_size(2)

    # 1. Miss on get
    route1 = Endpoint.get_pokemon(1)
    assert poke_cache.get(route1) is None
    assert poke_cache.stats.misses == 1
    assert poke_cache.stats.hits == 0

    # 2. Fetch (sets=1)
    await client.pokemon.fetch_pokemon(1)
    assert poke_cache.stats.sets == 1

    # 3. Hit on get
    assert poke_cache.get(route1) is not None
    assert poke_cache.stats.hits == 1
    assert math.isclose(poke_cache.stats.hit_ratio, 0.5, rel_tol=1e-9)

    # 4. Fill and trigger eviction
    await client.pokemon.fetch_pokemon(2)
    await client.pokemon.fetch_pokemon(3)
    assert poke_cache.stats.evictions == 1

    # 5. Group and Manager aggregate stats
    assert client.pokemon.cache_group.stats.hits >= 1
    assert client.http.cache_manager.stats.hits >= 1

    # 6. CacheStats __add__, sum(), and TypeError validation
    s1 = pokelance.CacheStats(hits=2, misses=1, sets=3, evictions=0)
    s2 = pokelance.CacheStats(hits=3, misses=2, sets=1, evictions=1)
    combined = s1 + s2
    assert combined.hits == 5
    assert combined.misses == 3
    assert combined.sets == 4
    assert combined.evictions == 1

    total_sum = sum([s1, s2], pokelance.CacheStats())
    assert total_sum.hits == 5

    with pytest.raises(TypeError, match="Cannot add CacheStats with"):
        _ = s1 + "invalid"  # type: ignore[operator]
