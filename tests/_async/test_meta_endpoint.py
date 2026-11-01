"""Singleton metadata fetching and caching, with and without registry warming."""

import pytest

import pokelance
from pokelance.endpoints import Endpoint
from pokelance.models import APIMetadata


@pytest.mark.asyncio
async def test_metadata_fetch_and_cache(client: pokelance.PokeLanceAsyncClient) -> None:
    assert client.utility.get_api_metadata() is None
    assert not hasattr(Endpoint, "get_api_metadata_endpoints")
    route = Endpoint.get_api_metadata()
    assert route.endpoint == "/meta"
    metadata = await client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    assert hasattr(metadata, "hash") and hasattr(metadata, "deploy_date")
    assert client.utility.get_api_metadata() is metadata
    assert client.utility.cache_group.api_metadata.get(route) is metadata


@pytest.mark.asyncio
async def test_metadata_after_registry_warming(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    assert cached_client.utility.cache_group.api_metadata.endpoints == {}
    metadata = await cached_client.utility.fetch_api_metadata()
    assert isinstance(metadata, APIMetadata)
    assert cached_client.utility.get_api_metadata() is metadata
