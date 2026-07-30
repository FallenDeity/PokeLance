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
- Extension.cache.<category>.endpoints is non-empty after cached_client is ready
- All extensions' categories with list-endpoints are populated after wait_until_ready()
"""
import typing as t

import pytest

import pokelance
from pokelance.cache import BaseCache
from pokelance.constants import ExtensionEnum
from pokelance.http import Endpoint

# ---------------------------------------------------------------------------
# wait_until_ready behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wait_until_ready_no_cache_completes(client: pokelance.PokeLance) -> None:
    """wait_until_ready with cache_endpoints=False should return without hanging."""
    await client.wait_until_ready()  # must not block


@pytest.mark.asyncio
async def test_wait_until_ready_with_cache(cached_client: pokelance.PokeLance) -> None:
    """cached_client fixture already called wait_until_ready; all tasks must be done."""
    assert not cached_client.http._tasks_queue, "All background tasks should be complete."


# ---------------------------------------------------------------------------
# Manual setup() per extension
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_populates_pokemon_endpoints(client: pokelance.PokeLance) -> None:
    await client.pokemon.setup()
    assert len(client.http.cache.pokemon.pokemon.endpoints) > 0
    assert len(client.http.cache.pokemon.pokemon_species.endpoints) > 0


@pytest.mark.asyncio
async def test_setup_populates_berry_endpoints(client: pokelance.PokeLance) -> None:
    await client.berry.setup()
    assert len(client.http.cache.berry.berry.endpoints) > 0
    assert len(client.http.cache.berry.berry_firmness.endpoints) > 0
    assert len(client.http.cache.berry.berry_flavor.endpoints) > 0


@pytest.mark.asyncio
async def test_setup_skips_categories_without_list_endpoint(client: pokelance.PokeLance) -> None:
    """
    utility.setup() should work even though api-metadata has no list endpoint.
    It must not raise, and the language endpoints should still be populated.
    """
    await client.utility.setup()
    assert len(client.http.cache.utility.language.endpoints) > 0


# ---------------------------------------------------------------------------
# All list-endpoint categories populated after wait_until_ready
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_list_endpoint_categories_populated(cached_client: pokelance.PokeLance) -> None:
    """
    For every ExtensionEnum value, iterate its categories. For each category
    that has a corresponding Endpoint.get_<category>_endpoints() classmethod,
    the backing BaseCache should have at least one endpoint registered.
    """
    exts = [e.value for e in ExtensionEnum]
    missing: t.List[str] = []
    for ext in exts:
        for category in ext.categories:
            list_endpoint_name = f"get_{category.replace('-', '_')}_endpoints"
            if not hasattr(Endpoint, list_endpoint_name):
                continue  # no list endpoint exists (api-metadata, etc.)
            cat_attr = category.replace("-", "_")
            ext_cache = getattr(cached_client, ext.name).cache
            sub_cache: BaseCache[t.Any, t.Any] = getattr(ext_cache, cat_attr)
            if not sub_cache.endpoints:
                missing.append(f"{ext.name}.{cat_attr}")
    assert not missing, f"These caches are empty after wait_until_ready: {missing}"


# ---------------------------------------------------------------------------
# load_documents() unit test (no network, pure mapping check)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_documents_populates_name_and_id(client: pokelance.PokeLance) -> None:
    """
    load_documents() should populate both name-keyed and id-keyed entries
    in the endpoint dict.
    """
    fake_results = [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
    ]
    cache = client.http.cache.pokemon.pokemon
    cache.load_documents(fake_results)

    assert "bulbasaur" in cache.endpoints
    assert "ivysaur" in cache.endpoints
    assert cache.endpoints["bulbasaur"].id == 1
    assert cache.endpoints["ivysaur"].id == 2


@pytest.mark.asyncio
async def test_load_documents_populates_reverse_id_index(client: pokelance.PokeLance) -> None:
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
    cache = client.http.cache.pokemon.pokemon
    cache.load_documents(fake_results)

    assert cache._endpoints_by_id["1"] == "bulbasaur"
    assert cache._endpoints_by_id["2"] == "ivysaur"


@pytest.mark.asyncio
async def test_secondary_type_cache_populates_reverse_id_index(client: pokelance.PokeLance) -> None:
    """
    SecondaryTypeCache keys `_endpoints` by id rather than name (these
    categories have no name field), so the reverse index maps id -> id for
    consistency with the same get() lookup path used by name-keyed caches.
    """
    fake_results = [
        {"name": "1", "url": "https://pokeapi.co/api/v2/machine/1/"},
        {"name": "2", "url": "https://pokeapi.co/api/v2/machine/2/"},
    ]
    cache = client.http.cache.machine.machine
    cache.load_documents(fake_results)

    assert "1" in cache.endpoints
    assert "2" in cache.endpoints
    assert cache._endpoints_by_id["1"] == "1"
    assert cache._endpoints_by_id["2"] == "2"


# ---------------------------------------------------------------------------
# load_all() fills the data cache from endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_all_fills_cache_after_setup(client: pokelance.PokeLance) -> None:
    """After setup() + load_all() the berry cache size should match the endpoint count."""
    await client.berry.setup()
    berry_cache = client.http.cache.berry.berry_flavor
    await berry_cache.load_all()
    assert len(berry_cache) == len(
        berry_cache.endpoints
    ), "After load_all(), every endpoint should have a cached entry."
