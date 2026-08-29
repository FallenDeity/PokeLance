"""
Tests for every standard sync extension endpoint (list + individual fetch/get).

Strategy
--------
For each ExtensionEnum category that has a list-endpoint:
  1. The endpoint registry is non-empty after sync_cached_client is ready.
  2. Pick a random name from that registry.
  3. fetch_<category>(name) returns a model and caches it.
  4. get_<category>(name) then returns the same model from cache (cache-hit).
"""

from __future__ import annotations

import concurrent.futures
import random
import typing as t

import pytest

from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint

if t.TYPE_CHECKING:
    import pokelance
    from pokelance.cache import SyncCache
    from pokelance.models import Berry, BerryFirmness, BerryFlavor, Move, Pokemon, Type

# ---------------------------------------------------------------------------
# Parametrised sweep: every category with a list-endpoint
# ---------------------------------------------------------------------------

_ENDPOINT_CATEGORIES: list[tuple[str, str]] = []
for _ext in ExtensionEnum:
    for _cat in _ext.value.categories:
        _list_name = f"get_{_cat.replace('-', '_')}_endpoints"
        if hasattr(Endpoint, _list_name):
            _ENDPOINT_CATEGORIES.append((_ext.name.lower(), _cat))


@pytest.mark.parametrize("ext_name,category", _ENDPOINT_CATEGORIES, ids=[f"{e}.{c}" for e, c in _ENDPOINT_CATEGORIES])
def test_sync_fetch_then_get_cache_hit(
    sync_cached_client: pokelance.PokeLanceSyncClient,
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
    ext_obj = getattr(sync_cached_client, ext_name)
    if not hasattr(ext_obj.cache_group, cat_attr):
        pytest.skip(f"{ext_name}.{cat_attr} is not in cache_group.")

    sub_cache: SyncCache[t.Any, t.Any] = getattr(ext_obj.cache_group, cat_attr)

    # 1. Endpoint registry populated
    assert sub_cache.endpoints, f"{ext_name}.{cat_attr} endpoint registry is empty."

    # 2. Pick a random endpoint entry; convert to int for numeric-only keys
    chosen = random.choice(list(sub_cache.endpoints.keys()))
    try:
        arg: str | int = int(chosen)
    except ValueError:
        arg = chosen

    # 3. fetch_ populates the data cache
    fetch_fn = getattr(ext_obj, f"fetch_{cat_attr}")
    result = fetch_fn(arg)
    assert result is not None, f"fetch_{cat_attr}({arg!r}) returned None."

    # 4. get_ returns the same object from cache
    get_fn = getattr(ext_obj, f"get_{cat_attr}")
    cached_result = get_fn(arg)
    assert cached_result is not None, f"get_{cat_attr}({arg!r}) returned None after fetch."

    # Value equality (model __eq__ compares fields, not identity)
    assert result == cached_result


# ---------------------------------------------------------------------------
# Spot-check known models to guard against regressions
# ---------------------------------------------------------------------------


def test_sync_fetch_pokemon_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    mon: Pokemon = sync_cached_client.pokemon.fetch_pokemon("bulbasaur")
    assert mon.name == "bulbasaur"
    assert mon.id == 1
    assert len(mon.abilities) > 0
    assert len(mon.types) > 0


def test_sync_fetch_berry_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    berry: Berry = sync_cached_client.berry.fetch_berry("cheri")
    assert berry.name == "cheri"
    assert berry.id == 1


def test_sync_fetch_berry_firmness_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    firmness: BerryFirmness = sync_cached_client.berry.fetch_berry_firmness("very-soft")
    assert firmness.name == "very-soft"


def test_sync_fetch_berry_flavor_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    flavor: BerryFlavor = sync_cached_client.berry.fetch_berry_flavor("spicy")
    assert flavor.name == "spicy"


def test_sync_fetch_move_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    move: Move = sync_cached_client.move.fetch_move("pound")
    assert move.name == "pound"
    assert move.id == 1


def test_sync_fetch_type_spot_check(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    type_: Type = sync_cached_client.pokemon.fetch_type("normal")
    assert type_.name == "normal"


# ---------------------------------------------------------------------------
# Concurrent fetches across extensions in threads
# ---------------------------------------------------------------------------


def test_sync_concurrent_fetches_across_extensions(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """
    Fetch from several extensions concurrently using a thread pool;
    confirm all results land in their respective caches.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        f_pokemon = executor.submit(sync_cached_client.pokemon.fetch_pokemon, 1)
        f_berry = executor.submit(sync_cached_client.berry.fetch_berry, 1)
        f_move = executor.submit(sync_cached_client.move.fetch_move, 1)
        f_type = executor.submit(sync_cached_client.pokemon.fetch_type, 1)

        pokemon = f_pokemon.result()
        berry = f_berry.result()
        move = f_move.result()
        type_ = f_type.result()

    assert pokemon.name == "bulbasaur"
    assert berry.name == "cheri"
    assert move.name == "pound"
    assert type_.name == "normal"

    # All should be in cache
    assert sync_cached_client.http.cache_manager.pokemon.pokemon.get(Endpoint.get_pokemon(1)) is not None
    assert sync_cached_client.http.cache_manager.berry.berry.get(Endpoint.get_berry(1)) is not None
    assert sync_cached_client.http.cache_manager.move.move.get(Endpoint.get_move(1)) is not None
    assert sync_cached_client.http.cache_manager.pokemon.type.get(Endpoint.get_type(1)) is not None


# ---------------------------------------------------------------------------
# getch_data sweep: all standard categories
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ext_name,category", _ENDPOINT_CATEGORIES, ids=[f"{e}.{c}" for e, c in _ENDPOINT_CATEGORIES])
def test_sync_getch_data_fetch_and_cache_hit(
    sync_cached_client: pokelance.PokeLanceSyncClient,
    ext_name: str,
    category: str,
) -> None:
    cat_attr = category.replace("-", "_")
    ext_obj = getattr(sync_cached_client, ext_name)
    if not hasattr(ext_obj.cache_group, cat_attr):
        pytest.skip(f"{ext_name}.{cat_attr} is not in cache_group.")

    sub_cache: SyncCache[t.Any, t.Any] = getattr(ext_obj.cache_group, cat_attr)

    if not sub_cache.endpoints:
        pytest.skip(f"{ext_name}.{cat_attr} has no endpoints loaded.")

    chosen = random.choice(list(sub_cache.endpoints.keys()))
    try:
        arg: str | int = int(chosen)
    except ValueError:
        arg = chosen

    result1: t.Any = sync_cached_client.getch_data(ext_name, category, arg)  # pyright: ignore[reportUnknownVariableType]
    assert result1 is not None

    result2: t.Any = sync_cached_client.getch_data(ext_name, category, arg)  # pyright: ignore[reportUnknownVariableType]
    assert result1 == result2
