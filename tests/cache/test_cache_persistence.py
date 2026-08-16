# pyright: reportPrivateUsage=false
"""
Tests for BaseCache.save() and BaseCache.load() using a real tempfs directory.

Isolation
---------
The `clear_all_caches` autouse fixture in conftest.py wipes all data caches
before each test. No manual clear() calls are needed here.

Coverage
--------
- save() creates the expected JSON file
- save() serialises a standard (single-object) cache entry correctly
- save() serialises a list-valued entry (location_area_encounter) correctly
- save() on empty cache writes an empty JSON object {}
- load() restores single-object entries into the same client
- load() adjusts max_size to the number of loaded entries
- Round-trip: fetch → save → load → get_ hits cache (no network call)
- Multiple categories saved and loaded independently
- List-valued (encounter) round-trip preserves field values
"""

import json
import os
import tempfile
import typing as t

import pytest

import pokelance
from pokelance.http import Endpoint
from pokelance.models import LocationAreaEncounter, Pokemon

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_json(path: str) -> dict[str, t.Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# save() file creation and content
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_creates_file(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.pokemon.fetch_pokemon(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{client.http.cache_manager.pokemon.pokemon._name}.json"
        assert os.path.exists(os.path.join(tmpdir, filename))


@pytest.mark.asyncio
async def test_save_content_single_object(client: pokelance.PokeLanceAsyncClient) -> None:
    # Cache is clean (cleared by autouse fixture), so exactly 3 entries will be saved.
    for i in (1, 2, 3):
        await client.pokemon.fetch_pokemon(i)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{client.http.cache_manager.pokemon.pokemon._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert len(data) == 3, f"Expected 3 entries, got {len(data)}."
    for v in data.values():
        assert isinstance(v, dict), "Standard cache values should serialise as dicts."


@pytest.mark.asyncio
async def test_save_content_list_valued(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """location_area_encounter stores a list confirm the JSON preserves that shape."""
    await cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        await cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)
        filename = f"{cached_client.http.cache_manager.pokemon.location_area_encounter._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert len(data) == 1
    endpoint_key = next(iter(data))
    assert "/encounters" in endpoint_key, "Key should contain the /encounters sub-path."
    assert isinstance(data[endpoint_key], list), "List-valued cache must serialise as a JSON array."
    assert len(data[endpoint_key]) > 0


@pytest.mark.asyncio
async def test_save_empty_cache_writes_empty_object(client: pokelance.PokeLanceAsyncClient) -> None:
    # Cache is clean nothing fetched, nothing to save.
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{client.http.cache_manager.pokemon.pokemon._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert data == {}, "Empty cache should serialise as an empty JSON object."


# ---------------------------------------------------------------------------
# load() single-object entries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_restores_single_objects(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.pokemon.fetch_pokemon(1)
    await client.pokemon.fetch_pokemon(2)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        # Clear then reload into the same client
        client.http.cache_manager.pokemon.pokemon.clear()
        await client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        assert len(client.http.cache_manager.pokemon.pokemon) == 2

        route1 = Endpoint.get_pokemon(1)
        cached: Pokemon | None = client.http.cache_manager.pokemon.pokemon.get(route1)
        assert cached is not None
        assert cached.name == "bulbasaur"


@pytest.mark.asyncio
async def test_load_adjusts_max_size(client: pokelance.PokeLanceAsyncClient) -> None:
    """After load(), max_size should expand if loaded entries exceed current max_size."""
    client.http.cache_manager.pokemon.pokemon.set_size(10)
    for i in range(1, 6):
        await client.pokemon.fetch_pokemon(i)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        client.http.cache_manager.pokemon.pokemon.clear()
        client.http.cache_manager.pokemon.pokemon.set_size(1)
        await client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        assert client.http.cache_manager.pokemon.pokemon._max_size == 5


# ---------------------------------------------------------------------------
# load() list-valued entries (location_area_encounter)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_restores_list_valued_entries(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    encounters_original = await cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        await cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)
        cached_client.http.cache_manager.pokemon.location_area_encounter.clear()
        await cached_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)

        route = Endpoint.get_location_area_encounter(1)
        cached = cached_client.http.cache_manager.pokemon.location_area_encounter.get(route)
        assert cached is not None, "Encounter list should be present after load."
        assert isinstance(cached, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in cached)
        assert len(cached) == len(encounters_original)


# ---------------------------------------------------------------------------
# Round-trip: fetch → save → load → verify cache hit (no extra network I/O)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_round_trip_cache_hit_after_load(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    After save → clear → load, get_pokemon() (cache-only, no network)
    should return the model directly.
    """
    await client.pokemon.fetch_pokemon(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        client.http.cache_manager.pokemon.pokemon.clear()
        # Seed the endpoint registry so _validate_resource passes for name lookups
        await client.pokemon.setup()
        await client.http.cache_manager.pokemon.pokemon.load(tmpdir)

        result = client.pokemon.get_pokemon("bulbasaur")
        assert result is not None
        assert result.name == "bulbasaur"


# ---------------------------------------------------------------------------
# Multiple categories saved and loaded independently
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_and_load_multiple_categories(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.pokemon.fetch_pokemon(1)
    await client.pokemon.fetch_pokemon_species(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        await client.http.cache_manager.pokemon.pokemon_species.save(tmpdir)

        filename_pk = f"{client.http.cache_manager.pokemon.pokemon._name}.json"
        filename_sp = f"{client.http.cache_manager.pokemon.pokemon_species._name}.json"
        assert os.path.exists(os.path.join(tmpdir, filename_pk))
        assert os.path.exists(os.path.join(tmpdir, filename_sp))

        client.http.cache_manager.pokemon.pokemon.clear()
        client.http.cache_manager.pokemon.pokemon_species.clear()
        await client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        await client.http.cache_manager.pokemon.pokemon_species.load(tmpdir)

        assert len(client.http.cache_manager.pokemon.pokemon) == 1
        assert len(client.http.cache_manager.pokemon.pokemon_species) == 1
