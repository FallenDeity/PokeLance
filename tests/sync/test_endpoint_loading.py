# pyright: reportPrivateUsage=false
"""Test sync registry loading, readiness waits, worker shutdown, and reconnects."""

from __future__ import annotations

import threading
import typing as t
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint, Route
from pokelance.exceptions import EndpointInitializationError

if t.TYPE_CHECKING:
    from pokelance.cache import SyncCache

# ---------------------------------------------------------------------------
# wait_until_ready behaviour
# ---------------------------------------------------------------------------


def test_sync_wait_until_ready_no_cache_raises(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """Disabled initialization raises at every readiness entry point without connecting."""
    group = sync_client.berry.cache_group
    for wait in (
        sync_client.wait_until_ready,
        sync_client.http.loader.wait_until_ready,
        sync_client.http.cache_manager.wait_until_ready,
        group.wait_until_ready,
        group.berry.wait_until_ready,
    ):
        with pytest.raises(RuntimeError, match="cache_endpoints=False"):
            wait()
    assert not sync_client.http.is_connected


def test_sync_partial_initialization_preserves_fetching(monkeypatch: pytest.MonkeyPatch) -> None:
    index_error = ValueError("index unavailable")

    def request(route: Route) -> dict[str, t.Any]:
        if route.endpoint == "/berry-firmness":
            raise index_error
        if route.payload is not None:
            return {"results": [{"name": "cheri", "url": f"{route.url}/1/"}]}
        return {"id": 1, "name": "cheri"}

    with pokelance.PokeLanceSyncClient(setup_logging=False) as client:
        monkeypatch.setattr(client.http, "request", Mock(side_effect=request))
        with pytest.raises(EndpointInitializationError, match="index unavailable") as failure:
            client.wait_until_ready()
        assert "berry" in failure.value.errors
        assert not client.http.loader.is_ready
        group = client.berry.cache_group
        assert group.berry.is_ready and group.berry_flavor.is_ready
        assert not group.berry_firmness.is_ready
        group.berry.wait_until_ready()
        for wait in (
            group.berry_firmness.wait_until_ready,
            group.wait_until_ready,
            client.http.cache_manager.wait_until_ready,
        ):
            with pytest.raises(EndpointInitializationError) as cache_failure:
                wait()
            assert cache_failure.value.errors["berry_firmness"] is index_error
        fetched = client.berry.fetch_berry_firmness(1)
        assert client.berry.get_berry_firmness(1) is fetched


def test_sync_interrupted_initialization_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    started, release, closing = (threading.Event() for _ in range(3))
    factory = Mock(side_effect=lambda **kwargs: ThreadPoolExecutor(max_workers=1))
    monkeypatch.setattr("pokelance.http._sync.concurrent.futures.ThreadPoolExecutor", factory)

    with pokelance.PokeLanceSyncClient(setup_logging=False) as client:
        client.ext_tasks[:] = [(client.berry.setup, "berry"), (client.utility.setup, "utility")]

        def request(route: Route) -> dict[str, t.Any]:
            started.set()
            assert release.wait(2)
            if client.http.is_closing:
                raise RuntimeError("HTTP client closing")
            return {"results": []}

        monkeypatch.setattr(client.http, "request", Mock(side_effect=request))
        shutdown = client.http.loader.shutdown

        def observed_shutdown() -> None:
            closing.set()
            shutdown()

        monkeypatch.setattr(client.http.loader, "shutdown", observed_shutdown)
        client.http.connect()
        closer = threading.Thread(target=client.close)
        try:
            assert started.wait(2)
            closer.start()
            assert closing.wait(2)
        finally:
            release.set()
            if closer.ident is not None:
                closer.join(2)
        assert not closer.is_alive()

        with pytest.raises(EndpointInitializationError):
            client.http.loader.wait_until_ready()
        for group in (client.berry.cache_group, client.utility.cache_group):
            for cache in group._walk_caches():
                assert cache._ready.wait(1), "Interrupted initialization must unblock category waits"
            with pytest.raises(EndpointInitializationError):
                group.wait_until_ready()

        request_mock = Mock(return_value={"results": []})
        monkeypatch.setattr(client.http, "request", request_mock)
        client.wait_until_ready()
        assert client.http.loader.is_ready
        assert all(
            cache.is_ready
            for group in (client.berry.cache_group, client.utility.cache_group)
            for cache in group._walk_caches()
        )
        assert request_mock.call_count == 4
        client.close()
        request_mock.reset_mock()
        client.wait_until_ready()
        request_mock.assert_not_called()


def test_sync_cache_group_wait_until_ready(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """Resetting a cache group, triggering setup, and waiting on cache_group ensures subcache readiness."""
    group = sync_cached_client.berry.cache_group
    group.reset()
    for cache in group._walk_caches():
        assert not cache.is_ready

    sync_cached_client.berry.setup()
    group.wait_until_ready()

    for cache in group._walk_caches():
        assert cache.is_ready
    assert "cheri" in group.berry.endpoints


# ---------------------------------------------------------------------------
# Manual setup() per extension
# ---------------------------------------------------------------------------


def test_sync_setup_populates_pokemon_endpoints(sync_client: pokelance.PokeLanceSyncClient) -> None:
    sync_client.pokemon.setup()
    assert len(sync_client.http.cache_manager.pokemon.pokemon.endpoints) > 0
    assert len(sync_client.http.cache_manager.pokemon.pokemon_species.endpoints) > 0


def test_sync_setup_skips_categories_without_list_endpoint(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """
    utility.setup() should work even though api-metadata has no list endpoint.
    It must not raise, and the language endpoints should still be populated.
    """
    sync_client.utility.setup()
    assert len(sync_client.http.cache_manager.utility.language.endpoints) > 0


# ---------------------------------------------------------------------------
# All list-endpoint categories populated after wait_until_ready
# ---------------------------------------------------------------------------


def test_sync_all_list_endpoint_categories_populated(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """
    For every ExtensionEnum value, iterate its categories. For each category
    that has a corresponding Endpoint.get_<category>_endpoints() classmethod,
    the backing BaseCache should have at least one endpoint registered.
    """
    sync_cached_client.http.cache_manager.wait_until_ready()
    assert sync_cached_client.http.loader.is_ready
    assert all(
        cache.is_ready
        for group in sync_cached_client.http.cache_manager._walk_aggregates()
        for cache in group._walk_caches()
    )
    exts = [e.value for e in ExtensionEnum]
    missing: list[str] = []
    for ext in exts:
        for category in ext.categories:
            list_endpoint_name = f"get_{category.replace('-', '_')}_endpoints"
            if not hasattr(Endpoint, list_endpoint_name):
                continue  # no list endpoint exists (api-metadata, etc.)
            cat_attr = category.replace("-", "_")
            ext_cache = getattr(sync_cached_client, ext.name).cache_group
            if not hasattr(ext_cache, cat_attr):
                continue
            sub_cache: SyncCache[t.Any, t.Any] = getattr(ext_cache, cat_attr)
            if not sub_cache.endpoints:
                missing.append(f"{ext.name}.{cat_attr}")
    assert not missing, f"These caches are empty after wait_until_ready: {missing}"


# ---------------------------------------------------------------------------
# load_all() fills the data cache from endpoints
# ---------------------------------------------------------------------------


def test_sync_load_all_fills_cache_after_setup(sync_client: pokelance.PokeLanceSyncClient) -> None:
    """After setup() + load_all() the berry cache size should match the endpoint count."""
    sync_client.berry.setup()
    berry_cache = sync_client.http.cache_manager.berry.berry_flavor
    berry_cache.load_all()
    assert len(berry_cache) == len(berry_cache.endpoints), (
        "After load_all(), every endpoint should have a cached entry."
    )
