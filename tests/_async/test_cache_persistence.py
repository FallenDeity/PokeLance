# pyright: reportPrivateUsage=false
"""Cache persistence: empty data, typed round-trips, capacity, and independent files."""

import asyncio
import json
import os
import tempfile
import typing as t

import pytest

import pokelance
from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter

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
async def test_save_empty_cache_writes_empty_object(client: pokelance.PokeLanceAsyncClient) -> None:
    # Cache is clean nothing fetched, nothing to save.
    with tempfile.TemporaryDirectory() as tmpdir:
        await client.http.cache_manager.pokemon.pokemon.save(tmpdir)
        filename = f"{client.http.cache_manager.pokemon.pokemon._name}.json"
        data = await asyncio.to_thread(_read_json, os.path.join(tmpdir, filename))
    assert data == {}, "Empty cache should serialise as an empty JSON object."


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
        data = await asyncio.to_thread(
            _read_json,
            os.path.join(tmpdir, f"{cached_client.http.cache_manager.pokemon.location_area_encounter._name}.json"),
        )
        assert set(data) == {"/pokemon/1/encounters"}
        assert isinstance(data["/pokemon/1/encounters"], list)
        assert data["/pokemon/1/encounters"] == [entry.raw for entry in encounters_original]
        cached_client.http.cache_manager.pokemon.location_area_encounter.clear()
        await cached_client.http.cache_manager.pokemon.location_area_encounter.load(tmpdir)

        route = Endpoint.get_location_area_encounter(1)
        cached = cached_client.http.cache_manager.pokemon.location_area_encounter.get(route)
        assert cached is not None, "Encounter list should be present after load."
        assert isinstance(cached, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in cached)
        assert cached == encounters_original


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
        data = await asyncio.to_thread(_read_json, os.path.join(tmpdir, "pokemon.json"))
        assert set(data) == {"/pokemon/1"}
        assert isinstance(data["/pokemon/1"], dict)
        assert data["/pokemon/1"]["name"] == "bulbasaur"
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
