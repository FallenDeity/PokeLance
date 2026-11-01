"""Fetch/get and getch_data coverage for every generated endpoint, plus concurrent requests."""

import asyncio
import typing as t

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint

if t.TYPE_CHECKING:
    from pokelance.cache import AsyncCache
    from pokelance.models import Pokemon

# ---------------------------------------------------------------------------
# Parametrised sweep: every category with a list-endpoint
# ---------------------------------------------------------------------------

# Build (ext_name, category) pairs at collection time.
# _ext.value gives the Extension object directly (same as __get__ attribute access).
_ENDPOINT_CATEGORIES: list[tuple[str, str]] = []
for _ext in ExtensionEnum:
    for _cat in _ext.value.categories:
        _list_name = f"get_{_cat.replace('-', '_')}_endpoints"
        if hasattr(Endpoint, _list_name):
            _ENDPOINT_CATEGORIES.append((_ext.name.lower(), _cat))


@pytest.mark.asyncio
@pytest.mark.parametrize("ext_name,category", _ENDPOINT_CATEGORIES, ids=[f"{e}.{c}" for e, c in _ENDPOINT_CATEGORIES])
async def test_fetch_then_get_cache_hit(
    cached_client: pokelance.PokeLanceAsyncClient,
    ext_name: str,
    category: str,
) -> None:
    """
    For each (extension, category):
      - endpoint registry must be non-empty
      - fetch_ populates the data cache
      - get_ returns the cached value immediately after
    """
    cat_attr = category.replace("-", "_")
    ext_obj = getattr(cached_client, ext_name)
    if not hasattr(ext_obj.cache_group, cat_attr):
        pytest.skip(f"{ext_name}.{cat_attr} is not in cache_group.")

    sub_cache: AsyncCache[t.Any, t.Any] = getattr(ext_obj.cache_group, cat_attr)

    # Endpoint registry must be populated.
    assert sub_cache.endpoints, f"{ext_name}.{cat_attr} endpoint registry is empty."

    # Use the first registered resource, converting numeric-only keys to IDs.
    #    (machines, evolution chains, contest effects, etc.)
    chosen = next(iter(sub_cache.endpoints))
    try:
        arg: str | int = int(chosen)
    except ValueError:
        arg = chosen

    # Fetch populates the data cache.
    fetch_fn = getattr(ext_obj, f"fetch_{cat_attr}")
    result = await fetch_fn(arg)
    assert result is not None, f"fetch_{cat_attr}({arg!r}) returned None."

    # Get returns the same object from cache.
    get_fn = getattr(ext_obj, f"get_{cat_attr}")
    cached_result = get_fn(arg)
    assert cached_result is not None, f"get_{cat_attr}({arg!r}) returned None after fetch."

    # Both cache-only entry points must reuse the fetched object.
    assert cached_result is result
    assert await cached_client.getch_data(ext_name, category, arg) is result
    sub_cache.clear()
    dispatched = await cached_client.getch_data(ext_name, category, arg)
    assert dispatched == result
    assert await cached_client.getch_data(ext_name, category, arg) is dispatched


# ---------------------------------------------------------------------------
# Spot-check known models to guard against regressions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_pokemon_spot_check(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    mon: Pokemon = await cached_client.pokemon.fetch_pokemon("bulbasaur")
    assert mon.name == "bulbasaur"
    assert mon.id == 1
    assert len(mon.abilities) > 0
    assert len(mon.types) > 0


# ---------------------------------------------------------------------------
# Concurrent fetches across extensions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_fetches_across_extensions(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """
    Fetch from several extensions concurrently; confirm no coroutine interference
    and that all results land in their respective caches.
    """
    results = await asyncio.gather(
        cached_client.pokemon.fetch_pokemon(1),
        cached_client.berry.fetch_berry(1),
        cached_client.move.fetch_move(1),
        cached_client.pokemon.fetch_type(1),
    )
    pokemon, berry, move, type_ = results
    assert pokemon.name == "bulbasaur"
    assert berry.name == "cheri"
    assert move.name == "pound"
    assert type_.name == "normal"

    # All should be in cache
    assert cached_client.http.cache_manager.pokemon.pokemon.get(Endpoint.get_pokemon(1)) is not None
    assert cached_client.http.cache_manager.berry.berry.get(Endpoint.get_berry(1)) is not None
    assert cached_client.http.cache_manager.move.move.get(Endpoint.get_move(1)) is not None
    assert cached_client.http.cache_manager.pokemon.type.get(Endpoint.get_type(1)) is not None
