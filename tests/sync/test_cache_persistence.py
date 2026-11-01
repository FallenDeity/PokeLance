# pyright: reportPrivateUsage=false
"""Cache persistence: empty data, typed round-trips, capacity, and independent files."""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
import typing as t

import pytest

from pokelance.cache.sync.base import SyncCache
from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter

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


def test_sync_save_empty_cache_writes_empty_object(sync_client: pokelance.PokeLanceSyncClient) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        sync_client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{sync_client.http.cache_manager.pokemon.pokemon._name}.json"
        data = _read_json(os.path.join(tmpdir, filename))
    assert data == {}, "Empty cache should serialise as an empty JSON object."


def test_sync_save_preserves_existing_file_when_replace_fails(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = SyncCache(name="pokemon")
    file_path = pathlib.Path(tmp_path) / "pokemon.json"
    file_path.write_text('{"old": true}', encoding="utf-8")

    def fail_replace(*_args: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr("pokelance.cache._base.os.replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        cache.save(str(tmp_path))

    assert _read_json(str(file_path)) == {"old": True}
    assert os.listdir(tmp_path) == ["pokemon.json"]


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
        data = _read_json(
            os.path.join(tmpdir, f"{sync_cached_client.http.cache_manager.pokemon.location_area_encounter._name}.json")
        )
        assert set(data) == {"/pokemon/1/encounters"}
        assert isinstance(data["/pokemon/1/encounters"], list)
        assert data["/pokemon/1/encounters"] == [entry.raw for entry in encounters_original]
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.clear()
        sync_cached_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)

        route = Endpoint.get_location_area_encounter(1)
        cached = sync_cached_client.http.cache_manager.pokemon.location_area_encounter.get(route)
        assert cached is not None, "Encounter list should be present after load."
        assert isinstance(cached, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in cached)
        assert cached == encounters_original


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
        data = _read_json(os.path.join(tmpdir, "pokemon.json"))
        assert set(data) == {"/pokemon/1"}
        assert isinstance(data["/pokemon/1"], dict)
        assert data["/pokemon/1"]["name"] == "bulbasaur"
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
