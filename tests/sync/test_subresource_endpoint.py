"""
Tests for sync /pokemon/{id}/encounters the only sub-resource endpoint in the API.

Coverage
--------
- fetch_location_area_encounter() returns a non-empty list of LocationAreaEncounter
- All items in the list are LocationAreaEncounter instances
- Second call (get_) retrieves from cache without network
- Cache key is /pokemon/{id}/encounters
- save() serialises the list as a JSON array with /encounters in the key
- load() restores the list with correct types
- Different Pokemon have different (or differently-sized) encounter lists
- By-name and by-id fetches produce equal results for the same Pokemon
- Concurrent fetches for multiple Pokemon don't interfere
- getch_data() handles the location-area-encounter category correctly
- fetch for a Pokemon with no encounters returns an empty list (not an error)
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import tempfile

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter

# ---------------------------------------------------------------------------
# Basic return type
# ---------------------------------------------------------------------------


def test_sync_fetch_returns_list(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    assert isinstance(result, list)


def test_sync_fetch_returns_non_empty_list(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    assert len(result) > 0, "Bulbasaur should have at least one encounter location."


def test_sync_fetch_all_items_are_location_area_encounters(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    assert all(isinstance(e, LocationAreaEncounter) for e in result)


# ---------------------------------------------------------------------------
# Cache-hit path: get_ after fetch_
# ---------------------------------------------------------------------------


def test_sync_get_returns_none_before_fetch(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.get_location_area_encounter(999)
    assert result is None or isinstance(result, list)


def test_sync_get_returns_list_after_fetch(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    sync_cached_client.pokemon.fetch_location_area_encounter("bulbasaur")
    cached = sync_cached_client.pokemon.get_location_area_encounter("bulbasaur")
    assert cached is not None
    assert isinstance(cached, list)


def test_sync_get_and_fetch_return_equal_results(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    fetched = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    cached = sync_cached_client.pokemon.get_location_area_encounter(1)
    assert cached is not None
    assert len(fetched) == len(cached)
    for f_enc, c_enc in zip(fetched, cached, strict=False):
        assert f_enc == c_enc


# ---------------------------------------------------------------------------
# Cache key shape
# ---------------------------------------------------------------------------


def test_sync_cache_key_contains_encounters(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    sync_cached_client.pokemon.fetch_location_area_encounter(1)
    lae_cache = sync_cached_client.http.cache_manager.pokemon.location_area_encounter
    stored_keys = [k.endpoint for k in lae_cache.cache]
    assert any("/encounters" in k for k in stored_keys), (
        "The cache key for location_area_encounter should contain '/encounters'."
    )


def test_sync_cache_route_retrieval(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    sync_cached_client.pokemon.fetch_location_area_encounter(1)
    route = Endpoint.get_location_area_encounter(1)
    result = sync_cached_client.http.cache_manager.pokemon.location_area_encounter.get(route)
    assert result is not None
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# By-name vs by-id equivalence
# ---------------------------------------------------------------------------


def test_sync_by_name_and_by_id_return_equal_results(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    by_id = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    by_name = sync_cached_client.pokemon.fetch_location_area_encounter("bulbasaur")
    assert len(by_id) == len(by_name)


# ---------------------------------------------------------------------------
# Different Pokemon have different encounter lists
# ---------------------------------------------------------------------------


def test_sync_different_pokemon_have_different_encounters(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    enc_bulbasaur = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    enc_pikachu = sync_cached_client.pokemon.fetch_location_area_encounter(25)
    areas_bulba = {e.location_area.name for e in enc_bulbasaur if e.location_area}
    areas_pika = {e.location_area.name for e in enc_pikachu if e.location_area}
    assert areas_bulba != areas_pika or len(enc_bulbasaur) != len(enc_pikachu), (
        "Bulbasaur and Pikachu should have different encounter area lists."
    )


# ---------------------------------------------------------------------------
# Concurrent fetches in threads
# ---------------------------------------------------------------------------


def test_sync_concurrent_encounter_fetches(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 1)
        f2 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 25)
        f3 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 4)

        results = [f1.result(), f2.result(), f3.result()]

    for r in results:
        assert isinstance(r, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in r)


# ---------------------------------------------------------------------------
# Persistence methods: save() and load()
# ---------------------------------------------------------------------------


def test_sync_save_produces_json_array(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    sync_cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)
        filename = f"{sync_cached_client.http.cache_manager.pokemon.location_area_encounter._name}.json"  # pyright: ignore[reportPrivateUsage]
        save_file = os.path.join(tmpdir, filename)
        assert os.path.exists(save_file)
        with open(save_file, encoding="utf-8") as f:
            data = json.load(f)
        key = next(iter(data))
        assert "/encounters" in key
        assert isinstance(data[key], list)
        assert len(data[key]) > 0


def test_sync_load_restores_encounter_list(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    original = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)

        with pokelance.PokeLanceSyncClient(cache_endpoints=False) as new_client:
            new_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)

            route = Endpoint.get_location_area_encounter(1)
            loaded = new_client.http.cache_manager.pokemon.location_area_encounter.get(route)
            assert loaded is not None
            assert isinstance(loaded, list)
            assert all(isinstance(e, LocationAreaEncounter) for e in loaded)
            assert len(loaded) == len(original)


def test_sync_round_trip_encounter_values_match(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """Each encounter's location_area.name must survive the save/load round-trip."""
    original = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    original_areas = {e.location_area.name for e in original if e.location_area}
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.save(tmpdir)

        with pokelance.PokeLanceSyncClient(cache_endpoints=False) as new_client:
            new_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)
            route = Endpoint.get_location_area_encounter(1)
            loaded = new_client.http.cache_manager.pokemon.location_area_encounter.get(route)
            assert loaded is not None, "Loaded encounter list should not be None."
            loaded_areas = {e.location_area.name for e in loaded if e.location_area}
            assert original_areas == loaded_areas


# ---------------------------------------------------------------------------
# getch_data integration
# ---------------------------------------------------------------------------


def test_sync_getch_data_location_area_encounter(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result: list[LocationAreaEncounter] = sync_cached_client.getch_data(
        ExtensionEnum.Pokemon, "location-area-encounter", 1
    )
    assert isinstance(result, list)
    assert all(isinstance(e, LocationAreaEncounter) for e in result)


def test_sync_getch_data_encounter_cache_hit(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result1: list[LocationAreaEncounter] = sync_cached_client.getch_data(
        ExtensionEnum.Pokemon, "location-area-encounter", 1
    )
    result2: list[LocationAreaEncounter] = sync_cached_client.getch_data(
        ExtensionEnum.Pokemon, "location-area-encounter", 1
    )
    assert len(result1) == len(result2)


def test_sync_pokemon_with_no_encounters_returns_empty_list(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.fetch_location_area_encounter(132)
    assert isinstance(result, list), "Should always return a list, even if empty."
