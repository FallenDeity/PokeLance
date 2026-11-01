"""
Tests for the top-level PokeLance client helpers.

Coverage
--------
- ping / latency sanity check
- getch_data: happy paths (int id, string name, random endpoint, cache-hit)
- getch_data: error paths (invalid resource, category, extension)
- from_url: happy path + error paths
- get_image / get_audio: bytes returned, cache-hit faster, error
- model __eq__
"""

import asyncio
import random
import time
from unittest.mock import AsyncMock, Mock

import niquests
import pytest

import pokelance
from pokelance.constants import DEFAULT_BASE_URL, ExtensionEnum, get_base_url
from pokelance.endpoints import Endpoint
from pokelance.exceptions import HTTPException, ImageNotFound, ResourceNotFound
from pokelance.http._async import AsyncHttpClient
from pokelance.models import Pokemon

# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_client_ping(client: pokelance.PokeLanceAsyncClient) -> None:
    ping = await client.ping()
    assert ping >= 0, "Ping value must be non-negative."


# ---------------------------------------------------------------------------
# getch_data happy paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_getch_data_by_id(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    assert pokemon.name == "bulbasaur"


@pytest.mark.asyncio
async def test_getch_data_by_name(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "bulbasaur")
    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "bulbasaur"


@pytest.mark.asyncio
async def test_getch_data_cache_hit(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """Second call must return the exact same model instance from cache."""
    result1: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    result2: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    assert result1 == result2


@pytest.mark.asyncio
async def test_getch_data_random_endpoint(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    """Fetch a random name from the endpoint registry; confirm it lands in cache."""
    id_ = random.choice(list(cached_client.pokemon.cache_group.pokemon.endpoints.keys()))
    pokemon: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", id_)
    assert pokemon.name == id_
    route = Endpoint.get_pokemon(id_)
    cached: Pokemon | None = cached_client.pokemon.cache_group.pokemon.get(route)
    assert cached is not None and cached.name == id_


# ---------------------------------------------------------------------------
# getch_data error paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_getch_data_invalid_resource(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ResourceNotFound):
        await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "does-not-exist-zzz")


@pytest.mark.asyncio
async def test_getch_data_invalid_category(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ValueError):
        await cached_client.getch_data(ExtensionEnum.Pokemon, "not-a-real-category", "bulbasaur")


@pytest.mark.asyncio
async def test_getch_data_invalid_extension(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ValueError):
        await cached_client.getch_data("NotAnExtension", "pokemon", "bulbasaur")


# ---------------------------------------------------------------------------
# from_url happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_from_url(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    id_ = random.choice(list(cached_client.pokemon.cache_group.pokemon.endpoints.keys()))
    pokemon: Pokemon = await cached_client.from_url(f"https://pokeapi.co/api/v2/pokemon/{id_}")
    assert pokemon.name == id_
    route = Endpoint.get_pokemon(id_)
    cached: Pokemon | None = cached_client.pokemon.cache_group.pokemon.get(route)
    assert cached is not None and cached.name == id_


# ---------------------------------------------------------------------------
# from_url error paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_from_url_invalid_resource(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ResourceNotFound):
        await cached_client.from_url("https://pokeapi.co/api/v2/pokemon/does-not-exist-zzz")


@pytest.mark.asyncio
async def test_from_url_invalid_category(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ValueError):
        await cached_client.from_url("https://pokeapi.co/api/v2/garbage/something")


@pytest.mark.asyncio
async def test_from_url_rejects_trailing_path(client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ValueError):
        await client.from_url("https://pokeapi.co/api/v2/pokemon/25/encounters/extra")


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_image_returns_bytes(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.sprites.front_default is not None
    img = await cached_client.get_image(pokemon.sprites.front_default)
    assert img and isinstance(img, bytes)


@pytest.mark.asyncio
async def test_get_image_cache_hit_is_faster(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await cached_client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    assert url is not None
    t0 = time.perf_counter()
    await cached_client.get_image(url)
    first = time.perf_counter() - t0
    t1 = time.perf_counter()
    await cached_client.get_image(url)
    second = time.perf_counter() - t1
    assert first > second, "Cached image fetch should be faster than the initial network fetch."


@pytest.mark.asyncio
async def test_get_image_invalid_url(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    with pytest.raises(ImageNotFound):
        await cached_client.get_image("https://pokeapi.co/api/v2/pokemon/invalid")


@pytest.mark.asyncio
async def test_get_audio_returns_bytes(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.cries.latest is not None
    audio = await cached_client.get_audio(pokemon.cries.latest)
    assert audio and isinstance(audio, bytes)


@pytest.mark.asyncio
async def test_get_audio_cache_hit_is_faster(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await cached_client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    assert url is not None
    t0 = time.perf_counter()
    await cached_client.get_audio(url)
    first = time.perf_counter() - t0
    t1 = time.perf_counter()
    await cached_client.get_audio(url)
    second = time.perf_counter() - t1
    assert first > second, "Cached audio fetch should be faster than the initial network fetch."


@pytest.mark.asyncio
async def test_media_transport_error_is_wrapped() -> None:
    url = "https://media.example/asset"
    transport_error = niquests.exceptions.RequestException("transport failed")
    session = Mock(request=AsyncMock(side_effect=transport_error))
    client = pokelance.PokeLanceAsyncClient(cache_endpoints=False, session=session, setup_logging=False)

    try:
        with pytest.raises(HTTPException) as exc_info:
            await client.http.load_image(url)
    finally:
        await client.close()

    assert exc_info.value.__cause__ is transport_error
    assert exc_info.value.route.url == url
    assert exc_info.value.status == -1


# ---------------------------------------------------------------------------
# Model equality
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_model_equality(cached_client: pokelance.PokeLanceAsyncClient) -> None:
    p1 = await cached_client.pokemon.fetch_pokemon(1)
    p2 = await cached_client.pokemon.fetch_pokemon(1)
    assert p1 == p2


@pytest.mark.asyncio
async def test_base_url_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    staging_url = "https://staging.pokeapi.co/api/v2"

    assert get_base_url() == DEFAULT_BASE_URL

    monkeypatch.setenv("POKEAPI_BASE_URL", staging_url)

    assert get_base_url() == staging_url

    async with pokelance.PokeLanceAsyncClient(cache_endpoints=False) as client:
        berry = await client.berry.fetch_berry(1)

        assert berry.item.url.startswith(staging_url)
        assert berry.name == "cheri"


# ---------------------------------------------------------------------------
# Lifecycle and State
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_client_context_manager() -> None:
    client = pokelance.PokeLanceAsyncClient(cache_endpoints=False)
    async with client as c:
        assert c.http is not None
        assert c.pokemon is not None


@pytest.mark.asyncio
async def test_async_client_manual_close() -> None:
    client = pokelance.PokeLanceAsyncClient(cache_endpoints=False)
    berry = await client.berry.fetch_berry(1)
    assert berry.name == "cheri"
    await client.close()
    assert client.http.session is None


@pytest.mark.asyncio
async def test_fetch_refreshes_cache(client: pokelance.PokeLanceAsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    request = AsyncMock(side_effect=[{"name": "old"}, {"name": "new"}, RuntimeError("request failed")])
    monkeypatch.setattr(client.http, "request", request)
    first = await client.berry.fetch_berry(1)
    second = await client.berry.fetch_berry(1)
    assert second is not first and second.name == "new"
    assert client.berry.get_berry(1) is second
    assert request.call_count == 2
    with pytest.raises(RuntimeError, match="request failed"):
        await client.berry.fetch_berry(1)
    assert client.berry.get_berry(1) is second


@pytest.mark.asyncio
@pytest.mark.parametrize("close_method", ["close", "context", "http"])
async def test_shutdown_drains_shared_media(monkeypatch: pytest.MonkeyPatch, close_method: str) -> None:
    image_started, audio_started = asyncio.Event(), asyncio.Event()
    image_cancelled, audio_cancelled = asyncio.Event(), asyncio.Event()

    async def load_image(http: AsyncHttpClient, url: str) -> bytes:
        if url == "safe":
            return b"image"
        image_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            image_cancelled.set()
        return b"image"

    async def load_audio(http: AsyncHttpClient, url: str) -> bytes:
        audio_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            audio_cancelled.set()
        return b"audio"

    monkeypatch.setattr(AsyncHttpClient, "load_image", load_image)
    monkeypatch.setattr(AsyncHttpClient, "load_audio", load_audio)
    client = pokelance.PokeLanceAsyncClient(cache_endpoints=False, setup_logging=False)
    other = pokelance.PokeLanceAsyncClient(cache_endpoints=False, setup_logging=False)

    def close_session() -> None:
        assert image_cancelled.is_set() and audio_cancelled.is_set()

    session = Mock(close=AsyncMock(side_effect=close_session))
    monkeypatch.setattr(client.http, "session", session)
    image = asyncio.create_task(client.get_image("url"))
    audio = asyncio.create_task(client.get_audio("url"))
    await image_started.wait()
    await audio_started.wait()
    other_image = asyncio.create_task(other.get_image("url"))
    await asyncio.sleep(0)
    if close_method == "context":
        await client.__aexit__(None, None, None)
    elif close_method == "http":
        await client.http.close()
    else:
        await client.close()
    for caller in (image, audio, other_image):
        with pytest.raises(asyncio.CancelledError):
            await caller
    assert client.get_image.cache_parameters()["tasks"] == 0
    assert client.get_audio.cache_parameters()["tasks"] == 0
    session.close.assert_awaited_once()
    assert not other.get_image.cache_parameters()["closed"]
    assert await other.get_image("safe") == b"image"
    await other.close()
