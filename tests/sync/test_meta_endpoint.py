"""
Tests for the sync /meta (api-metadata) endpoint the special case that:
  - Has NO list-endpoint (no Endpoint.get_api_metadata_endpoints())
  - Takes NO parameters (singleton resource)
  - Uses APIMetadataCache (a SecondaryTypeCache)
  - Should be gracefully skipped by setup() without raising
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pokelance.endpoints import Endpoint
from pokelance.models import APIMetadata

if TYPE_CHECKING:
    import pokelance

# ---------------------------------------------------------------------------
# Structural / registry assertions
# ---------------------------------------------------------------------------


def test_sync_api_metadata_has_no_list_endpoint() -> None:
    """There must be no get_api_metadata_endpoints classmethod on Endpoint."""
    assert not hasattr(Endpoint, "get_api_metadata_endpoints"), (
        "api-metadata must not have a list-endpoint; it is a singleton resource."
    )


def test_sync_api_metadata_has_direct_fetch_endpoint() -> None:
    """There must be a get_api_metadata() that returns /meta."""
    route = Endpoint.get_api_metadata()
    assert route.endpoint == "/meta"


# ---------------------------------------------------------------------------
# setup() graceful skip
# ---------------------------------------------------------------------------


def test_sync_utility_setup_does_not_raise(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """utility.setup() must complete without error even though api-metadata
    has no list-endpoint. The hasattr guard in _base.py should skip it cleanly."""
    sync_client.utility.setup()  # must not raise


def test_sync_utility_setup_still_loads_language(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """After setup(), language endpoints should be present even though
    api-metadata was skipped."""
    sync_client.utility.setup()
    assert len(sync_client.http.cache_manager.utility.language.endpoints) > 0


def test_sync_api_metadata_endpoints_registry_stays_empty_after_setup(
    sync_client: pokelance.PokeLanceSyncClient,
) -> None:
    """The api_metadata cache's endpoint registry should remain empty
    after setup() there is no list to load from."""
    sync_client.utility.setup()
    assert len(sync_client.http.cache_manager.utility.api_metadata.endpoints) == 0


# ---------------------------------------------------------------------------
# fetch / get behaviour
# ---------------------------------------------------------------------------


def test_sync_get_api_metadata_returns_none_before_fetch(sync_client: pokelance.PokeLanceSyncClient) -> None:
    result = sync_client.utility.get_api_metadata()
    assert result is None, "Cache should be cold before any fetch."


def test_sync_fetch_api_metadata_returns_model(sync_client: pokelance.PokeLanceSyncClient) -> None:
    metadata = sync_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)


def test_sync_fetch_api_metadata_has_expected_fields(sync_client: pokelance.PokeLanceSyncClient) -> None:
    metadata = sync_client.utility.fetch_api_metadata()
    assert hasattr(metadata, "hash"), "APIMetadata should have a 'hash' field."
    assert hasattr(metadata, "deploy_date"), "APIMetadata should have a 'deploy_date' field."


def test_sync_get_api_metadata_returns_model_after_fetch(sync_client: pokelance.PokeLanceSyncClient) -> None:
    sync_client.utility.fetch_api_metadata()
    result = sync_client.utility.get_api_metadata()
    assert result is not None, "Cache should be warm after fetch."
    assert isinstance(result, APIMetadata)


def test_sync_fetch_api_metadata_twice_returns_equal_models(sync_client: pokelance.PokeLanceSyncClient) -> None:
    meta1 = sync_client.utility.fetch_api_metadata()
    meta2 = sync_client.utility.fetch_api_metadata()
    assert meta1 == meta2, "Two consecutive fetches should return equal models."


# ---------------------------------------------------------------------------
# Cache key shape
# ---------------------------------------------------------------------------


def test_sync_api_metadata_cache_key_is_meta_route(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """The data must be stored under the /meta route, not under a
    /api-metadata/<id> style key."""
    sync_client.utility.fetch_api_metadata()
    route = Endpoint.get_api_metadata()
    result = sync_client.http.cache_manager.utility.api_metadata.get(route)
    assert result is not None, "APIMetadata should be retrievable via the /meta route."


# ---------------------------------------------------------------------------
# Interaction with sync_cached_client (full endpoint load)
# ---------------------------------------------------------------------------


def test_sync_api_metadata_works_alongside_cached_client(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """Even after wait_until_ready() (which triggers all setup tasks), fetching
    api-metadata should work normally."""
    metadata = sync_cached_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    # And get_ should now hit cache
    cached = sync_cached_client.utility.get_api_metadata()
    assert cached is not None
    assert cached == metadata
