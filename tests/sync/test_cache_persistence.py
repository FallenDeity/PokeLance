# pyright: reportPrivateUsage=false
"""
Tests for sync BaseCache.save() and BaseCache.load() using a real tempfs directory.

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

from __future__ import annotations

import json
import os
import tempfile
import typing as t

from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter, Pokemon

if t.TYPE_CHECKING:
    import pokelance

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_json(path: str) -> dict[str, t.Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# save() file creation and content
# ---------------------------------------------------------------------------


def test_sync_save_creates_file(sync_client: pokelance.PokeLanceSyncClient) -> None:
    sync_client.pokemon.fetch_pokemon(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{sync_client.http.cache_manager.pokemon.pokemon._name}.json"
        assert os.path.exists(os.path.join(tmpdir, filename))


def test_sync_save_content_single_object(sync_client: pokelance.PokeLanceSyncClient) -> None:
    for i in (1, 2, 3):
        sync_client.pokemon.fetch_pokemon(i)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{sync_client.http.cache_manager.pokemon.pokemon._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert len(data) == 3, f"Expected 3 entries, got {len(data)}."
    for v in data.values():
        assert isinstance(v, dict), "Standard cache values should serialise as dicts."


def test_sync_save_content_list_valued(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """location_area_encounter stores a list confirm the JSON preserves that shape."""
    sync_cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)
        filename = f"{sync_cached_client.http.cache_manager.pokemon.location_area_encounter._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert len(data) == 1
    endpoint_key = next(iter(data))
    assert "/encounters" in endpoint_key, "Key should contain the /encounters sub-path."
    assert isinstance(data[endpoint_key], list), "List-valued cache must serialise as a JSON array."
    assert len(data[endpoint_key]) > 0


def test_sync_save_empty_cache_writes_empty_object(sync_client: pokelance.PokeLanceSyncClient) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{sync_client.http.cache_manager.pokemon.pokemon._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert data == {}, "Empty cache should serialise as an empty JSON object."


# ---------------------------------------------------------------------------
# load() single-object entries
# ---------------------------------------------------------------------------


def test_sync_load_restores_single_objects(sync_client: pokelance.PokeLanceSyncClient) -> None:
    sync_client.pokemon.fetch_pokemon(1)
    sync_client.pokemon.fetch_pokemon(2)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        # Clear then reload into the same client
        sync_client.http.cache_manager.pokemon.pokemon.clear()
        sync_client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        assert len(sync_client.http.cache_manager.pokemon.pokemon) == 2

        route1 = Endpoint.get_pokemon(1)
        cached: Pokemon | None = sync_client.http.cache_manager.pokemon.pokemon.get(route1)
        assert cached is not None
        assert cached.name == "bulbasaur"


def test_sync_load_adjusts_max_size(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """After load(), max_size should expand if loaded entries exceed current max_size."""
    sync_client.http.cache_manager.pokemon.pokemon.set_size(10)
    for i in range(1, 6):
        sync_client.pokemon.fetch_pokemon(i)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        sync_client.http.cache_manager.pokemon.pokemon.clear()
        sync_client.http.cache_manager.pokemon.pokemon.set_size(1)
        sync_client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        assert sync_client.http.cache_manager.pokemon.pokemon._max_size == 5


# ---------------------------------------------------------------------------
# load() list-valued entries (location_area_encounter)
# ---------------------------------------------------------------------------


def test_sync_load_restores_list_valued_entries(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    encounters_original = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.clear()
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)

        route = Endpoint.get_location_area_encounter(1)
        cached = sync_cached_client.http.cache_manager.pokemon.location_area_encounter.get(route)
        assert cached is not None, "Encounter list should be present after load."
        assert isinstance(cached, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in cached)
        assert len(cached) == len(encounters_original)


# ---------------------------------------------------------------------------
# Round-trip: fetch → save → load → verify cache hit (no extra network I/O)
# ---------------------------------------------------------------------------


def test_sync_round_trip_cache_hit_after_load(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """
    After save → clear → load, get_pokemon() (cache-only, no network)
    should return the model directly.
    """
    sync_client.pokemon.fetch_pokemon(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        sync_client.http.cache_manager.pokemon.pokemon.clear()
        # Seed the endpoint registry so _validate_resource passes for name lookups
        sync_client.pokemon.setup()
        sync_client.http.cache_manager.pokemon.pokemon.load(tmpdir)

        result = sync_client.pokemon.get_pokemon("bulbasaur")
        assert result is not None
        assert result.name == "bulbasaur"


# ---------------------------------------------------------------------------
# Multiple categories saved and loaded independently
# ---------------------------------------------------------------------------


def test_sync_save_and_load_multiple_categories(sync_client: pokelance.PokeLanceSyncClient) -> None:
    sync_client.pokemon.fetch_pokemon(1)
    sync_client.pokemon.fetch_pokemon_species(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        sync_client.http.cache_manager.pokemon.pokemon_species.save(tmpdir)

        filename_pk = f"{sync_client.http.cache_manager.pokemon.pokemon._name}.json"
        filename_sp = f"{sync_client.http.cache_manager.pokemon.pokemon_species._name}.json"
        assert os.path.exists(os.path.join(tmpdir, filename_pk))
        assert os.path.exists(os.path.join(tmpdir, filename_sp))

        sync_client.http.cache_manager.pokemon.pokemon.clear()
        sync_client.http.cache_manager.pokemon.pokemon_species.clear()
        sync_client.http.cache_manager.pokemon.pokemon.load(tmpdir)
        sync_client.http.cache_manager.pokemon.pokemon_species.load(tmpdir)

        assert len(sync_client.http.cache_manager.pokemon.pokemon) == 1
        assert len(sync_client.http.cache_manager.pokemon.pokemon_species) == 1
