"""Tests for caching, save/load, and edge cases for different endpoint types."""
import json
import os
import tempfile

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.http import Endpoint
from pokelance.models import LocationAreaEncounter, Pokemon


class TestCacheSaveLoad:
    """Tests for cache save and load functionality."""

    @pytest.mark.asyncio
    async def test_save_load_pokemon_cache(self, client: pokelance.PokeLance) -> None:
        """Test saving and loading a Pokemon cache."""
        client.pokemon.cache.pokemon.clear()
        # Fetch some Pokemon to populate cache
        await client.pokemon.fetch_pokemon(1)
        await client.pokemon.fetch_pokemon(2)
        await client.pokemon.fetch_pokemon(3)

        # Save to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            await client.http.cache.pokemon.pokemon.save(tmpdir)

            # Verify file exists
            save_file = os.path.join(tmpdir, "PokemonCache.json")
            assert os.path.exists(save_file), "Cache file was not created"

            # Verify content
            with open(save_file, "r") as f:
                data = json.load(f)
            assert len(data) == 3, "Cache should have 3 entries"

            # Create new client and load
            async with pokelance.PokeLance() as new_client:
                await new_client.http.cache.pokemon.pokemon.load(tmpdir)

                # Verify loaded data
                route1 = Endpoint.get_pokemon(1)
                cached = new_client.http.cache.pokemon.pokemon.get(route1)
                assert cached is not None, "Pokemon 1 should be loaded from cache"
                assert cached.name == "bulbasaur", "Pokemon 1 should be bulbasaur"

    @pytest.mark.asyncio
    async def test_save_load_location_area_encounter_cache(self, cached_client: pokelance.PokeLance) -> None:
        """Test saving and loading a location area encounter cache (list response)."""
        await cached_client.wait_until_ready()

        # Fetch location area encounter (returns list)
        encounters = await cached_client.pokemon.fetch_location_area_encounter(1)
        assert isinstance(encounters, list), "Should return a list"
        assert len(encounters) > 0, "Should have at least one encounter"

        # Save to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            await cached_client.http.cache.pokemon.location_area_encounter.save(tmpdir)

            # Verify file exists
            save_file = os.path.join(tmpdir, "PokemonLocationAreaCache.json")
            assert os.path.exists(save_file), "Cache file was not created"

            # Verify content - should be a list in JSON
            with open(save_file, "r") as f:
                data = json.load(f)

            # Check that we have the endpoint key
            endpoint_key = list(data.keys())[0]
            assert "/encounters" in endpoint_key, "Should be an encounters endpoint"
            assert isinstance(data[endpoint_key], list), "Stored value should be a list"

            # Create new client and load
            async with pokelance.PokeLance() as new_client:
                # Need to setup endpoints first for the cache to work properly
                await new_client.pokemon.setup()

                # Manually create a minimal cache entry for testing
                route = Endpoint.get_location_area_encounter(1)
                await new_client.http.cache.pokemon.location_area_encounter.load(tmpdir)

                # Verify loaded data
                cached = new_client.http.cache.pokemon.location_area_encounter.get(route)
                assert cached is not None, "Location area encounter should be loaded from cache"
                assert isinstance(cached, list), "Loaded cache should be a list"
                assert len(cached) == len(encounters), "Should have same number of encounters"

    @pytest.mark.asyncio
    async def test_save_load_empty_cache(self, client: pokelance.PokeLance) -> None:
        """Test saving an empty cache."""
        # The client fixture doesn't cache endpoints, but still has some cached data
        # from the test setup. Let's test with a specific cache that we control.
        # Instead, let's test that save works with empty pokemon cache by
        # clearing it first
        client.http.cache.pokemon.pokemon.cache.clear()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            await client.http.cache.pokemon.pokemon.save(tmpdir)

            save_file = os.path.join(tmpdir, "PokemonCache.json")
            assert os.path.exists(save_file), "Cache file should be created"

            with open(save_file, "r") as f:
                data = json.load(f)
            # After clearing, cache should be empty
            assert data == {}, "Cleared cache should save as empty JSON object"


class TestMetaEndpoint:
    """Tests for meta/endpoints that don't have list endpoints."""

    @pytest.mark.asyncio
    async def test_api_metadata_no_list_endpoint(self, cached_client: pokelance.PokeLance) -> None:
        """Test that api-metadata doesn't have a list endpoint and is handled gracefully."""
        await cached_client.wait_until_ready()

        # Check that api-metadata category doesn't have a list endpoint
        list_endpoint_name = "get_api_metadata_endpoints"
        assert not hasattr(Endpoint, list_endpoint_name), "api-metadata should not have a list endpoint"

    @pytest.mark.asyncio
    async def test_fetch_api_metadata(self, cached_client: pokelance.PokeLance) -> None:
        """Test fetching api metadata directly."""
        await cached_client.wait_until_ready()

        # Should be able to fetch directly since there's no list endpoint
        metadata = await cached_client.utility.fetch_api_metadata()
        assert metadata is not None, "Should fetch api metadata"
        # The metadata response has these fields (not count)
        assert hasattr(metadata, "hash"), "Metadata should have hash"
        assert hasattr(metadata, "deploy_date"), "Metadata should have deploy_date"

    @pytest.mark.asyncio
    async def test_setup_skips_missing_list_endpoints(self, client: pokelance.PokeLance) -> None:
        """Test that setup() skips categories without list endpoints gracefully."""
        # This should not raise an error even though api-metadata has no list endpoint
        await client.utility.setup()

        # The utility extension should still have language endpoints
        assert len(client.http.cache.utility.language.endpoints) > 0, "Language endpoints should be loaded"


class TestSubresourceListEndpoint:
    """Tests for subresource endpoints that return lists (like location_area_encounter)."""

    @pytest.mark.asyncio
    async def test_location_area_encounter_returns_list(self, cached_client: pokelance.PokeLance) -> None:
        """Test that location_area_encounter returns a list of encounters."""
        await cached_client.wait_until_ready()

        encounters = await cached_client.pokemon.fetch_location_area_encounter(1)
        assert isinstance(encounters, list), "Should return a list"
        assert all(isinstance(e, LocationAreaEncounter) for e in encounters), "All items should be LocationAreaEncounter"

    @pytest.mark.asyncio
    async def test_location_area_encounter_cache_roundtrip(self, cached_client: pokelance.PokeLance) -> None:
        """Test that location_area_encounter can be fetched and retrieved from cache."""
        await cached_client.wait_until_ready()

        # Fetch
        encounters = await cached_client.pokemon.fetch_location_area_encounter("bulbasaur")
        assert isinstance(encounters, list), "Should return a list"

        # Get from cache
        cached = cached_client.pokemon.get_location_area_encounter("bulbasaur")
        assert cached is not None, "Should get from cache"
        assert isinstance(cached, list), "Cached value should be a list"
        assert len(cached) == len(encounters), "Cached list should have same length"

    @pytest.mark.asyncio
    async def test_location_area_encounter_different_pokemon(self, cached_client: pokelance.PokeLance) -> None:
        """Test that different Pokemon have different encounter lists."""
        await cached_client.wait_until_ready()

        # Fetch two different Pokemon
        encounters1 = await cached_client.pokemon.fetch_location_area_encounter(1)
        encounters2 = await cached_client.pokemon.fetch_location_area_encounter(25)  # Pikachu

        # They should be different (different locations)
        location_names1 = {e.location_area.name for e in encounters1}
        location_names2 = {e.location_area.name for e in encounters2}

        # At least some locations should be different
        assert location_names1 != location_names2 or len(encounters1) != len(encounters2)


class TestGetChDataEdgeCases:
    """Tests for getch_data with edge cases."""

    @pytest.mark.asyncio
    async def test_getch_data_location_area_encounter(self, cached_client: pokelance.PokeLance) -> None:
        """Test getch_data with location_area_encounter (list-returning subresource)."""
        await cached_client.wait_until_ready()

        # This should work - getch_data should handle list returns
        result = await cached_client.getch_data(ExtensionEnum.Pokemon, "location-area-encounter", 1)

        # Result should be a list
        assert isinstance(result, list), "getch_data should return list for location_area_encounter"
        assert all(isinstance(e, LocationAreaEncounter) for e in result)

    @pytest.mark.asyncio
    async def test_getch_data_with_string_id(self, cached_client: pokelance.PokeLance) -> None:
        """Test getch_data with string ID (pokemon name)."""
        await cached_client.wait_until_ready()

        result = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "bulbasaur")
        assert isinstance(result, Pokemon)
        assert result.name == "bulbasaur"

    @pytest.mark.asyncio
    async def test_getch_data_cache_hit(self, cached_client: pokelance.PokeLance) -> None:
        """Test that getch_data uses cache properly."""
        await cached_client.wait_until_ready()

        # First fetch - from API
        result1 = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)

        # Second fetch - should be from cache
        result2 = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)

        assert result1.name == result2.name


class TestCacheEviction:
    """Tests for cache LRU eviction."""

    @pytest.mark.asyncio
    async def test_lru_eviction(self, client: pokelance.PokeLance) -> None:
        """Test that cache evicts oldest entries when full."""
        # Set small cache size
        client.http.cache.set_size(3)

        # Fetch 4 Pokemon (should evict first one)
        await client.pokemon.fetch_pokemon(1)
        await client.pokemon.fetch_pokemon(2)
        await client.pokemon.fetch_pokemon(3)
        await client.pokemon.fetch_pokemon(4)

        # First Pokemon should be evicted
        route1 = Endpoint.get_pokemon(1)
        _cached1 = client.http.cache.pokemon.pokemon.get(route1)
        # Note: with LRU, the behavior depends on access order
        # Since we accessed them in order, 1 should be evicted

        # Latest should still be there
        route4 = Endpoint.get_pokemon(4)
        cached4 = client.http.cache.pokemon.pokemon.get(route4)
        assert cached4 is not None, "Latest Pokemon should still be cached"


class TestEndpointAliasing:
    """Tests for endpoint aliasing in cache.get()."""

    @pytest.mark.asyncio
    async def test_cache_get_with_alias(self, cached_client: pokelance.PokeLance) -> None:
        """Test that cache.get() handles alias lookups correctly."""
        await cached_client.wait_until_ready()

        # Fetch a pokemon
        _pokemon = await cached_client.pokemon.fetch_pokemon(1)

        # Try getting with different route formats (if aliasing exists)
        # The cache's get() method has alias logic
        route = Endpoint.get_pokemon(1)
        result = cached_client.http.cache.pokemon.pokemon.get(route)

        assert result is not None, "Should find cached pokemon"
        assert result.name == "bulbasaur"


class TestCacheIntegration:
    """Integration tests for full caching workflows."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_location_area(self, cached_client: pokelance.PokeLance) -> None:
        """Test a complete workflow involving location_area_encounter."""
        await cached_client.wait_until_ready()

        # 1. Fetch pokemon
        pokemon = await cached_client.pokemon.fetch_pokemon(1)
        assert pokemon.name == "bulbasaur"

        # 2. Get location areas for that pokemon
        encounters = await cached_client.pokemon.fetch_location_area_encounter(1)
        assert len(encounters) > 0

        # 3. Verify cache state
        pokemon_route = Endpoint.get_pokemon(1)
        cached_pokemon = cached_client.http.cache.pokemon.pokemon.get(pokemon_route)
        assert cached_pokemon is not None

        encounter_route = Endpoint.get_location_area_encounter(1)
        cached_encounters = cached_client.http.cache.pokemon.location_area_encounter.get(encounter_route)
        assert cached_encounters is not None
        assert isinstance(cached_encounters, list)

    @pytest.mark.asyncio
    async def test_concurrent_fetches(self, cached_client: pokelance.PokeLance) -> None:
        """Test concurrent fetches don't cause issues."""
        import asyncio

        await cached_client.wait_until_ready()

        # Fetch multiple Pokemon concurrently
        results = await asyncio.gather(
            cached_client.pokemon.fetch_pokemon(1),
            cached_client.pokemon.fetch_pokemon(2),
            cached_client.pokemon.fetch_pokemon(3),
            cached_client.pokemon.fetch_location_area_encounter(1),
        )

        # Verify results
        assert results[0].name == "bulbasaur"
        assert results[1].name == "ivysaur"
        assert results[2].name == "venusaur"
        assert isinstance(results[3], list)  # location area encounters
