"""Encounter list models, cache aliases, concurrent fetches, and empty results."""

import asyncio

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter


@pytest.mark.asyncio
async def test_encounter_fetch_and_cache(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    assert cached_client.pokemon.get_location_area_encounter(1) is None
    result = await cached_client.pokemon.fetch_location_area_encounter(1)
    assert isinstance(result, list) and result
    assert all(isinstance(item, LocationAreaEncounter) for item in result)
    assert cached_client.pokemon.get_location_area_encounter(1) is result
    assert cached_client.pokemon.get_location_area_encounter("bulbasaur") is result
    route = Endpoint.get_location_area_encounter(1)
    cache = cached_client.pokemon.cache_group.location_area_encounter
    assert route.endpoint == "/pokemon/1/encounters"
    assert cache.get(route) is result
    assert await cached_client.pokemon.fetch_location_area_encounter("bulbasaur") == result


@pytest.mark.asyncio
async def test_concurrent_encounter_fetches(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    results = await asyncio.gather(
        cached_client.pokemon.fetch_location_area_encounter(1),
        cached_client.pokemon.fetch_location_area_encounter(25),
        cached_client.pokemon.fetch_location_area_encounter(4),
    )
    for r in results:
        assert isinstance(r, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in r)


@pytest.mark.asyncio
async def test_getch_data_encounter_cache_hit(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    result: list[LocationAreaEncounter] = await cached_client.getch_data(
        ExtensionEnum.Pokemon, "location-area-encounter", 1
    )
    assert result and all(isinstance(item, LocationAreaEncounter) for item in result)
    assert await cached_client.getch_data(ExtensionEnum.Pokemon, "location-area-encounter", 1) is result


@pytest.mark.asyncio
async def test_pokemon_with_no_encounters_returns_empty_list(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    result = await cached_client.pokemon.fetch_location_area_encounter(10034)
    assert result == []
    assert cached_client.pokemon.get_location_area_encounter(10034) is result
