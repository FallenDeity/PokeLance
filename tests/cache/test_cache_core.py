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
import pytest

import pokelance
from pokelance.http import Endpoint

# ---------------------------------------------------------------------------
# Size / attributes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_default_max_size(client: pokelance.PokeLance) -> None:
    assert client.http.cache.max_size == 100


@pytest.mark.asyncio
async def test_cache_set_size_global(client: pokelance.PokeLance) -> None:
    client.http.cache.set_size(255)
    assert client.http.cache.max_size == 255
    assert client.http.cache.pokemon.pokemon._max_size == 255


@pytest.mark.asyncio
async def test_cache_set_size_per_category(client: pokelance.PokeLance) -> None:
    client.http.cache.pokemon.pokemon.set_size(42)
    assert client.http.cache.pokemon.pokemon._max_size == 42


@pytest.mark.asyncio
async def test_cache_client_backref(client: pokelance.PokeLance) -> None:
    assert client.http.cache.client is client


# ---------------------------------------------------------------------------
# LRU eviction
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_lru_eviction_drops_oldest(client: pokelance.PokeLance) -> None:
    """With max_size=3, fetching a 4th entry should evict the first."""
    client.http.cache.set_size(3)
    for i in range(1, 4):
        await client.pokemon.fetch_pokemon(i)
    assert len(client.http.cache.pokemon.pokemon) == 3

    await client.pokemon.fetch_pokemon(4)
    assert len(client.http.cache.pokemon.pokemon) == 3
    route4 = Endpoint.get_pokemon(4)
    assert client.http.cache.pokemon.pokemon.get(route4) is not None


@pytest.mark.asyncio
async def test_lru_access_refreshes_order(client: pokelance.PokeLance) -> None:
    """Re-accessing entry 1 after 2 and 3 keeps it alive when 4 is inserted."""
    client.http.cache.set_size(3)
    await client.pokemon.fetch_pokemon(1)
    await client.pokemon.fetch_pokemon(2)
    await client.pokemon.fetch_pokemon(3)

    # Touch entry 1 → it becomes MRU; entry 2 becomes LRU
    _ = client.http.cache.pokemon.pokemon[Endpoint.get_pokemon(1)]

    await client.pokemon.fetch_pokemon(4)
    route1 = Endpoint.get_pokemon(1)
    route2 = Endpoint.get_pokemon(2)
    assert client.http.cache.pokemon.pokemon.get(route1) is not None, "Entry 1 should survive after re-access."
    assert client.http.cache.pokemon.pokemon.get(route2) is None, "Entry 2 should be evicted as the true LRU."


@pytest.mark.asyncio
async def test_lru_tracks_latest_entry(client: pokelance.PokeLance) -> None:
    """The most-recently-added entry should be last in the ordered dict."""
    client.http.cache.set_size(10)
    for i in range(1, 11):
        await client.pokemon.fetch_pokemon(i)
    latest = await client.pokemon.fetch_pokemon(25)
    keys = list(client.http.cache.pokemon.pokemon.cache.keys())
    last_value = client.http.cache.pokemon.pokemon.cache[keys[-1]]
    assert latest == last_value


# ---------------------------------------------------------------------------
# Alias resolution in cache.get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_get_by_id_after_name_fetch(cached_client: pokelance.PokeLance) -> None:
    """Fetch by name → retrieve by numeric id via alias lookup."""
    await cached_client.pokemon.fetch_pokemon("bulbasaur")
    route_by_id = Endpoint.get_pokemon(1)
    result = cached_client.http.cache.pokemon.pokemon.get(route_by_id)
    assert result is not None, "Should resolve bulbasaur via its numeric id alias."
    assert result.name == "bulbasaur"


@pytest.mark.asyncio
async def test_cache_get_by_name_after_id_fetch(cached_client: pokelance.PokeLance) -> None:
    """Fetch by id → retrieve by name via alias lookup."""
    await cached_client.pokemon.fetch_pokemon(1)
    route_by_name = Endpoint.get_pokemon("bulbasaur")
    result = cached_client.http.cache.pokemon.pokemon.get(route_by_name)
    assert result is not None, "Should resolve id=1 via bulbasaur name alias."
    assert result.name == "bulbasaur"


# ---------------------------------------------------------------------------
# Mapping protocol: __len__ and clear()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_len_increases_on_fetch(client: pokelance.PokeLance) -> None:
    assert len(client.http.cache.pokemon.pokemon) == 0
    await client.pokemon.fetch_pokemon(1)
    assert len(client.http.cache.pokemon.pokemon) == 1
    await client.pokemon.fetch_pokemon(2)
    assert len(client.http.cache.pokemon.pokemon) == 2


@pytest.mark.asyncio
async def test_cache_clear(client: pokelance.PokeLance) -> None:
    await client.pokemon.fetch_pokemon(1)
    assert len(client.http.cache.pokemon.pokemon) == 1
    client.http.cache.pokemon.pokemon.clear()
    assert len(client.http.cache.pokemon.pokemon) == 0


# ---------------------------------------------------------------------------
# alru_cache for images and audio
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_image_cache_contains(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    await client.get_image_async(url)
    assert client.get_image_async.__contains__(client, url)


@pytest.mark.asyncio
async def test_image_cache_clear(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    await client.get_image_async(url)
    client.get_image_async.cache_clear()
    assert not client.get_image_async.__contains__(client, url)


@pytest.mark.asyncio
async def test_image_cache_set_size(client: pokelance.PokeLance) -> None:
    client.get_image_async.set_size(10)
    assert client.get_image_async.cache_info().maxsize == 10


@pytest.mark.asyncio
async def test_audio_cache_contains(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    await client.get_audio_async(url)
    assert client.get_audio_async.__contains__(client, url)


@pytest.mark.asyncio
async def test_audio_cache_clear(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    await client.get_audio_async(url)
    client.get_audio_async.cache_clear()
    assert not client.get_audio_async.__contains__(client, url)


@pytest.mark.asyncio
async def test_audio_cache_set_size(client: pokelance.PokeLance) -> None:
    client.get_audio_async.set_size(10)
    assert client.get_audio_async.cache_info().maxsize == 10
