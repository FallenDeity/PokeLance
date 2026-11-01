"""Encounter list models, cache aliases, concurrent fetches, and empty results."""

import concurrent.futures

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint
from pokelance.models import LocationAreaEncounter


def test_sync_encounter_fetch_and_cache(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    assert sync_cached_client.pokemon.get_location_area_encounter(1) is None
    result = sync_cached_client.pokemon.fetch_location_area_encounter(1)
    assert isinstance(result, list) and result
    assert all(isinstance(item, LocationAreaEncounter) for item in result)
    assert sync_cached_client.pokemon.get_location_area_encounter(1) is result
    assert sync_cached_client.pokemon.get_location_area_encounter("bulbasaur") is result
    route = Endpoint.get_location_area_encounter(1)
    cache = sync_cached_client.pokemon.cache_group.location_area_encounter
    assert route.endpoint == "/pokemon/1/encounters"
    assert cache.get(route) is result
    assert sync_cached_client.pokemon.fetch_location_area_encounter("bulbasaur") == result


def test_sync_concurrent_encounter_fetches(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 1)
        f2 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 25)
        f3 = executor.submit(sync_cached_client.pokemon.fetch_location_area_encounter, 4)

        results = [f1.result(), f2.result(), f3.result()]

    for r in results:
        assert isinstance(r, list)
        assert all(isinstance(e, LocationAreaEncounter) for e in r)


def test_sync_getch_data_encounter_cache_hit(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result: list[LocationAreaEncounter] = sync_cached_client.getch_data(
        ExtensionEnum.Pokemon, "location-area-encounter", 1
    )
    assert result and all(isinstance(item, LocationAreaEncounter) for item in result)
    assert sync_cached_client.getch_data(ExtensionEnum.Pokemon, "location-area-encounter", 1) is result


def test_sync_pokemon_with_no_encounters_returns_empty_list(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_cached_client.pokemon.fetch_location_area_encounter(10034)
    assert result == []
    assert sync_cached_client.pokemon.get_location_area_encounter(10034) is result
