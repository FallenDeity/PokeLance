# pyright: reportPrivateUsage=false
"""Test async registry loading, readiness waits, cancellation, and reconnects."""

import asyncio
import typing as t
from unittest.mock import AsyncMock, Mock

import pytest

import pokelance
from pokelance.constants import ExtensionEnum
from pokelance.endpoints import Endpoint, Route
from pokelance.exceptions import EndpointInitializationError

if t.TYPE_CHECKING:
    from pokelance.cache import AsyncCache

# ---------------------------------------------------------------------------
# wait_until_ready behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wait_until_ready_no_cache_raises(client: pokelance.PokeLanceAsyncClient) -> None:
    """Disabled initialization raises at every readiness entry point without connecting."""
    group = client.berry.cache_group
    for wait in (
        client.wait_until_ready,
        client.http.loader.wait_until_ready,
        client.http.cache_manager.wait_until_ready,
        group.wait_until_ready,
        group.berry.wait_until_ready,
    ):
        with pytest.raises(RuntimeError, match="cache_endpoints=False"):
            await wait()
    assert not client.http.is_connected


@pytest.mark.asyncio
async def test_partial_initialization_preserves_fetching(monkeypatch: pytest.MonkeyPatch) -> None:
    index_error = ValueError("index unavailable")

    def request(route: Route) -> dict[str, t.Any]:
        if route.endpoint == "/berry-firmness":
            raise index_error
        if route.payload is not None:
            return {"results": [{"name": "cheri", "url": f"{route.url}/1/"}]}
        return {"id": 1, "name": "cheri"}

    async with pokelance.PokeLanceAsyncClient(setup_logging=False) as client:
        monkeypatch.setattr(client.http, "request", AsyncMock(side_effect=request))
        with pytest.raises(EndpointInitializationError, match="index unavailable") as failure:
            await client.wait_until_ready()
        assert "berry" in failure.value.errors
        assert not client.http.loader.is_ready
        group = client.berry.cache_group
        assert group.berry.is_ready and group.berry_flavor.is_ready
        assert not group.berry_firmness.is_ready
        await group.berry.wait_until_ready()
        for wait in (
            group.berry_firmness.wait_until_ready,
            group.wait_until_ready,
            client.http.cache_manager.wait_until_ready,
        ):
            with pytest.raises(EndpointInitializationError) as cache_failure:
                await wait()
            assert cache_failure.value.errors["berry_firmness"] is index_error
        fetched = await client.berry.fetch_berry_firmness(1)
        assert client.berry.get_berry_firmness(1) is fetched


@pytest.mark.asyncio
@pytest.mark.parametrize("before_start", [False, True])
async def test_cancelled_initialization_unblocks_waits_and_retries(
    monkeypatch: pytest.MonkeyPatch, before_start: bool
) -> None:
    started = asyncio.Event()

    async def blocked(route: Route) -> dict[str, t.Any]:
        started.set()
        await asyncio.Event().wait()
        return {"results": []}

    async with pokelance.PokeLanceAsyncClient(setup_logging=False) as client:
        client.ext_tasks[:] = [(client.berry.setup, "berry")]
        monkeypatch.setattr(client.http, "request", AsyncMock(side_effect=blocked))
        await client.http.connect()
        category_wait = asyncio.create_task(client.berry.cache_group.berry.wait_until_ready())
        if before_start:
            await client.http.loader.cancel_tasks()
            assert not started.is_set()
        else:
            await asyncio.wait_for(started.wait(), timeout=1)
        await client.close()

        with pytest.raises(EndpointInitializationError, match="cancelled"):
            await asyncio.wait_for(category_wait, timeout=1)
        for wait in (
            client.berry.cache_group.wait_until_ready,
            client.http.loader.wait_until_ready,
        ):
            with pytest.raises(EndpointInitializationError, match="cancelled"):
                await asyncio.wait_for(wait(), timeout=1)
        assert not client.http.loader.is_ready

        request = AsyncMock(return_value={"results": []})
        monkeypatch.setattr(client.http, "request", request)
        await asyncio.wait_for(client.wait_until_ready(), timeout=1)
        assert client.http.loader.is_ready
        assert all(cache.is_ready for cache in client.berry.cache_group._walk_caches())
        assert request.await_count == 3

        await client.close()
        request.reset_mock()
        await client.wait_until_ready()
        request.assert_not_awaited()


@pytest.mark.asyncio
async def test_shutdown_during_registry_request_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    started, release_request, draining, release_media = (asyncio.Event() for _ in range(4))

    async with pokelance.PokeLanceAsyncClient(setup_logging=False) as client:
        client.ext_tasks[:] = [(client.berry.setup, "berry")]

        async def request(route: Route) -> dict[str, t.Any]:
            started.set()
            await release_request.wait()
            if client.http.is_closing:
                raise RuntimeError("HTTP client closing")
            return {"results": []}

        async def drain() -> None:
            draining.set()
            await release_media.wait()

        monkeypatch.setattr(client.http, "request", AsyncMock(side_effect=request))
        monkeypatch.setattr(client, "get_image", Mock(cache_close=AsyncMock(side_effect=drain)))
        await client.http.connect()
        await asyncio.wait_for(started.wait(), timeout=1)
        closer = asyncio.create_task(client.close())
        try:
            await asyncio.wait_for(draining.wait(), timeout=1)
            release_request.set()
            with pytest.raises(EndpointInitializationError):
                await asyncio.wait_for(client.http.loader.wait_until_ready(), timeout=1)
        finally:
            release_media.set()
            await closer
        request_mock = AsyncMock(return_value={"results": []})
        monkeypatch.setattr(client.http, "request", request_mock)
        await asyncio.wait_for(client.wait_until_ready(), timeout=1)
        assert client.http.loader.is_ready
        assert request_mock.await_count == 3


@pytest.mark.asyncio
async def test_cancelled_readiness_wait_preserves_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    started, release = asyncio.Event(), asyncio.Event()

    async def request(route: Route) -> dict[str, t.Any]:
        started.set()
        await release.wait()
        return {"results": []}

    async with pokelance.PokeLanceAsyncClient(setup_logging=False) as client:
        client.ext_tasks[:] = [(client.berry.setup, "berry")]
        monkeypatch.setattr(client.http, "request", AsyncMock(side_effect=request))
        waiter = asyncio.create_task(client.wait_until_ready())
        await asyncio.wait_for(started.wait(), timeout=1)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        release.set()
        await asyncio.wait_for(client.wait_until_ready(), timeout=1)
        assert client.http.loader.is_ready


@pytest.mark.asyncio
async def test_cache_group_wait_until_ready(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """Resetting a cache group, triggering setup, and waiting on cache_group ensures subcache readiness."""
    group = cached_client.berry.cache_group
    group.reset()
    for cache in group._walk_caches():
        assert not cache.is_ready

    await cached_client.berry.setup()
    await group.wait_until_ready()

    for cache in group._walk_caches():
        assert cache.is_ready
    assert "cheri" in group.berry.endpoints


# ---------------------------------------------------------------------------
# Manual setup() per extension
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_populates_pokemon_endpoints(client: pokelance.PokeLanceAsyncClient) -> None:
    await client.pokemon.setup()
    assert len(client.http.cache_manager.pokemon.pokemon.endpoints) > 0
    assert len(client.http.cache_manager.pokemon.pokemon_species.endpoints) > 0


@pytest.mark.asyncio
async def test_setup_skips_categories_without_list_endpoint(client: pokelance.PokeLanceAsyncClient) -> None:
    """
    utility.setup() should work even though api-metadata has no list endpoint.
    It must not raise, and the language endpoints should still be populated.
    """
    await client.utility.setup()
    assert len(client.http.cache_manager.utility.language.endpoints) > 0


# ---------------------------------------------------------------------------
# All list-endpoint categories populated after wait_until_ready
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_list_endpoint_categories_populated(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """
    For every ExtensionEnum value, iterate its categories. For each category
    that has a corresponding Endpoint.get_<category>_endpoints() classmethod,
    the backing BaseCache should have at least one endpoint registered.
    """
    await cached_client.http.cache_manager.wait_until_ready()
    assert cached_client.http.loader.is_ready
    assert all(
        cache.is_ready
        for group in cached_client.http.cache_manager._walk_aggregates()
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
            ext_cache = getattr(cached_client, ext.name).cache_group
            if not hasattr(ext_cache, cat_attr):
                continue
            sub_cache: AsyncCache[t.Any, t.Any] = getattr(ext_cache, cat_attr)
            if not sub_cache.endpoints:
                missing.append(f"{ext.name}.{cat_attr}")
    assert not missing, f"These caches are empty after wait_until_ready: {missing}"


# ---------------------------------------------------------------------------
# load_all() fills the data cache from endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_all_fills_cache_after_setup(client: pokelance.PokeLanceAsyncClient) -> None:
    """After setup() + load_all() the berry cache size should match the endpoint count."""
    await client.berry.setup()
    berry_cache = client.http.cache_manager.berry.berry_flavor
    await berry_cache.load_all()
    assert len(berry_cache) == len(berry_cache.endpoints), (
        "After load_all(), every endpoint should have a cached entry."
    )
