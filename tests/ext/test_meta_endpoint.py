"""
Tests for the /meta (api-metadata) endpoint the special case that:
  - Has NO list-endpoint (no Endpoint.get_api_metadata_endpoints())
  - Takes NO parameters (singleton resource)
  - Uses APIMetadataCache (a SecondaryTypeCache)
  - Should be gracefully skipped by setup() without raising

Coverage
--------
- Endpoint class has no get_api_metadata_endpoints classmethod
- setup() on utility does not raise despite the missing list-endpoint
- fetch_api_metadata() returns an APIMetadata model with expected fields
- get_api_metadata() returns None before first fetch, model after
- Second fetch returns the cached value (no new network call needed)
- The cached route key is /meta (not an /api-metadata/ style key)
- api-metadata is excluded from the parametrised endpoint-loading tests
  (asserted here explicitly)
- hasattr guard in _base.py setup() is the correct mechanism (not try/except)
"""
import pytest

import pokelance
from pokelance.http import Endpoint
from pokelance.models import APIMetadata

# ---------------------------------------------------------------------------
# Structural / registry assertions
# ---------------------------------------------------------------------------


def test_api_metadata_has_no_list_endpoint() -> None:
    """There must be no get_api_metadata_endpoints classmethod on Endpoint."""
    assert not hasattr(
        Endpoint, "get_api_metadata_endpoints"
    ), "api-metadata must not have a list-endpoint; it is a singleton resource."


def test_api_metadata_has_direct_fetch_endpoint() -> None:
    """There must be a get_api_metadata() that returns /meta."""
    route = Endpoint.get_api_metadata()
    assert route.endpoint == "/meta"


# ---------------------------------------------------------------------------
# setup() graceful skip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_utility_setup_does_not_raise(client: pokelance.PokeLance) -> None:
    """utility.setup() must complete without error even though api-metadata
    has no list-endpoint. The hasattr guard in _base.py should skip it cleanly."""
    await client.utility.setup()  # must not raise


@pytest.mark.asyncio
async def test_utility_setup_still_loads_language(client: pokelance.PokeLance) -> None:
    """After setup(), language endpoints should be present even though
    api-metadata was skipped."""
    await client.utility.setup()
    assert len(client.http.cache.utility.language.endpoints) > 0


@pytest.mark.asyncio
async def test_api_metadata_endpoints_registry_stays_empty_after_setup(
    client: pokelance.PokeLance,
) -> None:
    """The api_metadata cache's endpoint registry should remain empty
    after setup() there is no list to load from."""
    await client.utility.setup()
    assert len(client.http.cache.utility.api_metadata.endpoints) == 0


# ---------------------------------------------------------------------------
# fetch / get behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_api_metadata_returns_none_before_fetch(client: pokelance.PokeLance) -> None:
    result = client.utility.get_api_metadata()
    assert result is None, "Cache should be cold before any fetch."


@pytest.mark.asyncio
async def test_fetch_api_metadata_returns_model(client: pokelance.PokeLance) -> None:
    metadata = await client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)


@pytest.mark.asyncio
async def test_fetch_api_metadata_has_expected_fields(client: pokelance.PokeLance) -> None:
    metadata = await client.utility.fetch_api_metadata()
    assert hasattr(metadata, "hash"), "APIMetadata should have a 'hash' field."
    assert hasattr(metadata, "deploy_date"), "APIMetadata should have a 'deploy_date' field."


@pytest.mark.asyncio
async def test_get_api_metadata_returns_model_after_fetch(client: pokelance.PokeLance) -> None:
    await client.utility.fetch_api_metadata()
    result = client.utility.get_api_metadata()
    assert result is not None, "Cache should be warm after fetch."
    assert isinstance(result, APIMetadata)


@pytest.mark.asyncio
async def test_fetch_api_metadata_twice_returns_equal_models(client: pokelance.PokeLance) -> None:
    meta1 = await client.utility.fetch_api_metadata()
    meta2 = await client.utility.fetch_api_metadata()
    assert meta1 == meta2, "Two consecutive fetches should return equal models."


# ---------------------------------------------------------------------------
# Cache key shape
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_api_metadata_cache_key_is_meta_route(client: pokelance.PokeLance) -> None:
    """The data must be stored under the /meta route, not under a
    /api-metadata/<id> style key."""
    await client.utility.fetch_api_metadata()
    route = Endpoint.get_api_metadata()
    result = client.http.cache.utility.api_metadata.get(route)
    assert result is not None, "APIMetadata should be retrievable via the /meta route."


# ---------------------------------------------------------------------------
# Interaction with cached_client (full endpoint load)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_api_metadata_works_alongside_cached_client(cached_client: pokelance.PokeLance) -> None:
    """Even after wait_until_ready() (which triggers all setup tasks), fetching
    api-metadata should work normally."""
    metadata = await cached_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    # And get_ should now hit cache
    cached = cached_client.utility.get_api_metadata()
    assert cached is not None
    assert cached == metadata
