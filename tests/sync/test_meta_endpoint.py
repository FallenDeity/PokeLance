"""Singleton metadata fetching and caching, with and without registry warming."""

import pokelance
from pokelance.endpoints import Endpoint
from pokelance.models import APIMetadata


def test_sync_metadata_fetch_and_cache(sync_client: pokelance.PokeLanceSyncClient) -> None:
    assert sync_client.utility.get_api_metadata() is None
    assert not hasattr(Endpoint, "get_api_metadata_endpoints")
    route = Endpoint.get_api_metadata()
    assert route.endpoint == "/meta"
    metadata = sync_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    assert hasattr(metadata, "hash") and hasattr(metadata, "deploy_date")
    assert sync_client.utility.get_api_metadata() is metadata
    assert sync_client.utility.cache_group.api_metadata.get(route) is metadata


def test_sync_metadata_after_registry_warming(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    assert sync_cached_client.utility.cache_group.api_metadata.endpoints == {}
    metadata = sync_cached_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    assert sync_cached_client.utility.get_api_metadata() is metadata
