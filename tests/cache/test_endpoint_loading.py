# pyright: reportPrivateUsage=false
"""
Tests for endpoint-registry population (the list-endpoint side of caching).

Coverage
--------
- wait_until_ready() with cache_endpoints=False completes immediately
- wait_until_ready() with cache_endpoints=True waits for all tasks to finish
- setup() on an individual extension populates its endpoint registries
- setup() gracefully skips categories that have no list-endpoint
  (i.e. api-metadata and location-area-encounter share the /pokemon list)
- load_documents() correctly populates name→Endpoint and id→Endpoint mappings
- Extension.cache_group.<category>.endpoints is non-empty after cached_client is ready
- All extensions' categories with list-endpoints are populated after wait_until_ready()
"""

import typing as t

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.http import Endpoint

if t.TYPE_CHECKING:
    from pokelance.cache import AsyncCache

# ---------------------------------------------------------------------------
# wait_until_ready behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wait_until_ready_no_cache_completes(client: pokelance.PokeLanceAsyncClient) -> None:
    """wait_until_ready with cache_endpoints=False should return without hanging."""
    await client.wait_until_ready()  # must not block


def test_wait_until_ready_with_cache(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """cached_client fixture already called wait_until_ready; loader must be ready."""
    assert cached_client.http.loader.is_ready, "All background tasks should be complete."
    assert not cached_client.http.loader._tasks, "No background tasks should remain."


# ---------------------------------------------------------------------------
# Manual setup() per extension
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_populates_pokemon_endpoints(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.pokemon.setup()
    assert len(client.http.cache_manager.pokemon.pokemon.endpoints) > 0
    assert len(client.http.cache_manager.pokemon.pokemon_species.endpoints) > 0


@pytest.mark.asyncio
async def test_setup_populates_berry_endpoints(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.berry.setup()
    assert len(client.http.cache_manager.berry.berry.endpoints) > 0
    assert len(client.http.cache_manager.berry.berry_firmness.endpoints) > 0
    assert len(client.http.cache_manager.berry.berry_flavor.endpoints) > 0


@pytest.mark.asyncio
async def test_setup_skips_categories_without_list_endpoint(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    utility.setup() should work even though api-metadata has no list endpoint.
    It must not raise, and the language endpoints should still be populated.
    """
    await client.utility.setup()
    assert len(client.http.cache_manager.utility.language.endpoints) > 0


# ---------------------------------------------------------------------------
# All list-endpoint categories populated after wait_until_ready
# ---------------------------------------------------------------------------


def test_all_list_endpoint_categories_populated(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """
    For every ExtensionEnum value, iterate its categories. For each category
    that has a corresponding Endpoint.get_<category>_endpoints() classmethod,
    the backing BaseCache should have at least one endpoint registered.
    """
    exts = [e.value for e in ExtensionEnum]
    missing: list[str] = []
    for ext in exts:
        for category in ext.categories:
            list_endpoint_name = f"get_{category.replace('-', '_')}_endpoints"
            if not hasattr(Endpoint, list_endpoint_name):
                continue  # no list endpoint exists (api-metadata, etc.)
            cat_attr = category.replace("-", "_")
            ext_cache = getattr(cached_client, ext.name).cache_group
            if not hasattr(ext_cache, cat_attr):
                continue
            sub_cache: AsyncCache[t.Any, t.Any] = getattr(ext_cache, cat_attr)
            if not sub_cache.endpoints:
                missing.append(f"{ext.name}.{cat_attr}")
    assert not missing, f"These caches are empty after wait_until_ready: {missing}"


# ---------------------------------------------------------------------------
# load_documents() unit test (no network, pure mapping check)
# ---------------------------------------------------------------------------


def test_load_documents_populates_name_and_id(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    load_documents() should populate both name-keyed and id-keyed entries
    in the endpoint dict.
    """
    fake_results = [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
    ]
    cache = client.http.cache_manager.pokemon.pokemon
    cache.load_documents(fake_results)

    assert "bulbasaur" in cache.endpoints
    assert "ivysaur" in cache.endpoints
    assert cache.endpoints["bulbasaur"].id == 1
    assert cache.endpoints["ivysaur"].id == 2


def test_load_documents_populates_reverse_id_index(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    load_documents() should also populate _endpoints_by_id, the reverse index
    BaseCache.get() uses for alias resolution. Previously this reverse mapping
    was rebuilt from scratch (inverting the whole `_endpoints` dict) on every
    single get() miss; it should now be a standing index built once here.
    """
    fake_results = [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
    ]
    cache = client.http.cache_manager.pokemon.pokemon
    cache.load_documents(fake_results)

    assert cache._endpoints_by_id["1"] == "bulbasaur"
    assert cache._endpoints_by_id["2"] == "ivysaur"


def test_secondary_type_cache_populates_reverse_id_index(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    SecondaryTypeCache keys `_endpoints` by id rather than name (these
    categories have no name field), so the reverse index maps id -> id for
    consistency with the same get() lookup path used by name-keyed caches.
    """
    fake_results = [
        {"name": "1", "url": "https://pokeapi.co/api/v2/machine/1/"},
        {"name": "2", "url": "https://pokeapi.co/api/v2/machine/2/"},
    ]
    cache = client.http.cache_manager.machine.machine
    cache.load_documents(fake_results)

    assert "1" in cache.endpoints
    assert "2" in cache.endpoints
    assert cache._endpoints_by_id["1"] == "1"
    assert cache._endpoints_by_id["2"] == "2"


# ---------------------------------------------------------------------------
# reset_endpoints() allows safe reload
# ---------------------------------------------------------------------------


def test_reset_endpoints_clears_registry_and_rearms_event(client: pokelance.PokeLanceAsyncClient) -> None:
    """reset_endpoints() must clear all endpoint metadata."""
    cache = client.pokemon.cache_group.pokemon
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    assert cache._endpoints_cached
    assert "bulbasaur" in cache.endpoints

    cache.reset_endpoints()

    assert not cache._endpoints_cached
    assert cache._endpoints == {}
    assert cache._endpoints_by_id == {}
    assert cache._identifiers == set()


def test_load_documents_after_reset_replaces_registry(client: pokelance.PokeLanceAsyncClient) -> None:
    """After reset_endpoints(), load_documents() can re-populate cleanly."""
    cache = client.pokemon.cache_group.pokemon
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    cache.reset_endpoints()
    cache.load_documents(
        [
            {"name": "charmander", "url": "https://pokeapi.co/api/v2/pokemon/4/"},
            {"name": "squirtle", "url": "https://pokeapi.co/api/v2/pokemon/7/"},
        ]
    )
    assert "charmander" in cache.endpoints
    assert "squirtle" in cache.endpoints
    assert "bulbasaur" not in cache.endpoints, "stale entry from previous load must be gone"
    assert cache._endpoints_cached


def test_reset_endpoints_on_secondary_type_cache(client: pokelance.PokeLanceAsyncClient) -> None:
    """reset_endpoints() works on SecondaryTypeCache (machine) too."""
    cache = client.machine.cache_group.machine
    cache.load_documents([{"name": "1", "url": "https://pokeapi.co/api/v2/machine/1/"}])
    cache.reset_endpoints()
    assert cache._endpoints == {}
    cache.load_documents([{"name": "2", "url": "https://pokeapi.co/api/v2/machine/2/"}])
    assert "2" in cache.endpoints
    assert "1" not in cache.endpoints


@pytest.mark.asyncio
async def test_reset_endpoints_blocks_wait_until_ready(client: pokelance.PokeLanceAsyncClient) -> None:
    """After reset_endpoints(), setup() can re-populate endpoints cleanly."""
    cache = client.pokemon.cache_group.pokemon
    cache.load_documents([{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}])
    assert cache._endpoints_cached

    cache.reset_endpoints()
    assert not cache._endpoints_cached

    await client.pokemon.setup()
    assert "charmander" in cache.endpoints


# ---------------------------------------------------------------------------
# load_all() fills the data cache from endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_all_fills_cache_after_setup(client: pokelance.PokeLanceAsyncClient) -> None:
    """After setup() + load_all() the berry cache size should match the endpoint count."""
    await client.berry.setup()
    berry_cache = client.http.cache_manager.berry.berry_flavor
    await berry_cache.load_all()
    assert len(berry_cache) == len(berry_cache.endpoints), (
        "After load_all(), every endpoint should have a cached entry."
    )
