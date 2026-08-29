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

import random
import time

import pytest

import pokelance
from pokelance.constants import DEFAULT_BASE_URL, ExtensionEnum, get_base_url
from pokelance.endpoints import Endpoint
from pokelance.exceptions import ImageNotFound, ResourceNotFound
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
