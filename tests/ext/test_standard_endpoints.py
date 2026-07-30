"""
Tests for every standard extension endpoint (list + individual fetch/get).

Strategy
--------
For each ExtensionEnum category that has a list-endpoint:
  1. The endpoint registry is non-empty after cached_client is ready.
  2. Pick a random name from that registry.
  3. fetch_<category>(name) returns a model and caches it.
  4. get_<category>(name) then returns the same model from cache (cache-hit).

Additionally, a cross-extension concurrent-fetch smoke test is included.

Note on ExtensionEnum access
----------------------------
ExtensionEnum inherits BaseEnum which overrides __get__ to return self.value.
This means attribute-style access (ExtensionEnum.Pokemon) gives the Extension
value object directly, while item-style access (ExtensionEnum["Pokemon"]) gives
the raw enum member. getch_data() accepts the value object OR a plain string;
we use plain strings to avoid the __getitem__ vs __get__ ambiguity entirely.
"""
import asyncio
import random
import typing as t

import pytest

import pokelance
from pokelance.cache import BaseCache
from pokelance.constants import ExtensionEnum
from pokelance.http import Endpoint
from pokelance.models import Berry, BerryFirmness, BerryFlavor, Move, Pokemon, Type

# ---------------------------------------------------------------------------
# Parametrised sweep: every category with a list-endpoint
# ---------------------------------------------------------------------------

# Build (ext_name, category) pairs at collection time.
# _ext.value gives the Extension object directly (same as __get__ attribute access).
_ENDPOINT_CATEGORIES: t.List[t.Tuple[str, str]] = []
for _ext in ExtensionEnum:
    for _cat in _ext.value.categories:
        _list_name = f"get_{_cat.replace('-', '_')}_endpoints"
        if hasattr(Endpoint, _list_name):
            _ENDPOINT_CATEGORIES.append((_ext.name.lower(), _cat))


@pytest.mark.asyncio
@pytest.mark.parametrize("ext_name,category", _ENDPOINT_CATEGORIES, ids=[f"{e}.{c}" for e, c in _ENDPOINT_CATEGORIES])
async def test_fetch_then_get_cache_hit(
    cached_client: pokelance.PokeLance,
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
    sub_cache: BaseCache[t.Any, t.Any] = getattr(ext_obj.cache, cat_attr)

    # 1. Endpoint registry populated
    assert sub_cache.endpoints, f"{ext_name}.{cat_attr} endpoint registry is empty."

    # 2. Pick a random endpoint entry; convert to int for numeric-only keys
    #    (machines, evolution chains, contest effects, etc.)
    chosen = random.choice(list(sub_cache.endpoints.keys()))
    try:
        arg: t.Union[str, int] = int(chosen)
    except ValueError:
        arg = chosen

    # 3. fetch_ populates the data cache
    fetch_fn = getattr(ext_obj, f"fetch_{cat_attr}")
    result = await fetch_fn(arg)
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


@pytest.mark.asyncio
async def test_fetch_pokemon_spot_check(cached_client: pokelance.PokeLance) -> None:
    mon: Pokemon = await cached_client.pokemon.fetch_pokemon("bulbasaur")
    assert mon.name == "bulbasaur"
    assert mon.id == 1
    assert len(mon.abilities) > 0
    assert len(mon.types) > 0


@pytest.mark.asyncio
async def test_fetch_berry_spot_check(cached_client: pokelance.PokeLance) -> None:
    berry: Berry = await cached_client.berry.fetch_berry("cheri")
    assert berry.name == "cheri"
    assert berry.id == 1


@pytest.mark.asyncio
async def test_fetch_berry_firmness_spot_check(cached_client: pokelance.PokeLance) -> None:
    firmness: BerryFirmness = await cached_client.berry.fetch_berry_firmness("very-soft")
    assert firmness.name == "very-soft"


@pytest.mark.asyncio
async def test_fetch_berry_flavor_spot_check(cached_client: pokelance.PokeLance) -> None:
    flavor: BerryFlavor = await cached_client.berry.fetch_berry_flavor("spicy")
    assert flavor.name == "spicy"


@pytest.mark.asyncio
async def test_fetch_move_spot_check(cached_client: pokelance.PokeLance) -> None:
    move: Move = await cached_client.move.fetch_move("pound")
    assert move.name == "pound"
    assert move.id == 1


@pytest.mark.asyncio
async def test_fetch_type_spot_check(cached_client: pokelance.PokeLance) -> None:
    type_: Type = await cached_client.pokemon.fetch_type("normal")
    assert type_.name == "normal"


# ---------------------------------------------------------------------------
# Concurrent fetches across extensions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_fetches_across_extensions(cached_client: pokelance.PokeLance) -> None:
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
    assert cached_client.http.cache.pokemon.pokemon.get(Endpoint.get_pokemon(1)) is not None
    assert cached_client.http.cache.berry.berry.get(Endpoint.get_berry(1)) is not None
    assert cached_client.http.cache.move.move.get(Endpoint.get_move(1)) is not None
    assert cached_client.http.cache.pokemon.type.get(Endpoint.get_type(1)) is not None


# ---------------------------------------------------------------------------
# getch_data sweep: all standard categories
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("ext_name,category", _ENDPOINT_CATEGORIES, ids=[f"{e}.{c}" for e, c in _ENDPOINT_CATEGORIES])
async def test_getch_data_fetch_and_cache_hit(
    cached_client: pokelance.PokeLance,
    ext_name: str,
    category: str,
) -> None:
    """
    getch_data() must:
      1. Return a result for a valid name from the registry.
      2. Return an equal result on a second call (cache-hit path).

    We pass ext as a plain string so getch_data uses its str branch
    (ExtensionEnum.get_categories), avoiding the __getitem__ vs __get__
    ambiguity of ExtensionEnum member access.
    """
    cat_attr = category.replace("-", "_")
    ext_obj = getattr(cached_client, ext_name)
    sub_cache: BaseCache[t.Any, t.Any] = getattr(ext_obj.cache, cat_attr)

    if not sub_cache.endpoints:
        pytest.skip(f"{ext_name}.{cat_attr} has no endpoints loaded.")

    chosen = random.choice(list(sub_cache.endpoints.keys()))
    try:
        arg: t.Union[str, int] = int(chosen)
    except ValueError:
        arg = chosen

    # Pass ext_name as a plain string getch_data handles title-casing internally
    result1: t.Any = await cached_client.getch_data(ext_name, category, arg)
    assert result1 is not None

    result2: t.Any = await cached_client.getch_data(ext_name, category, arg)
    assert result1 == result2
