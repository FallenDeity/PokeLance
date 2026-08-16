"""
Tests for the top-level PokeLance sync client helpers.

Coverage
--------
- ping / latency sanity check
- getch_data: happy paths (int id, string name, random endpoint, cache-hit)
- getch_data: error paths (invalid resource, category, extension)
- from_url: happy path + error paths
- get_image / get_audio: bytes returned, cache-hit faster, error
- model __eq__
- base_url env var support
"""

from __future__ import annotations

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


def test_sync_client_ping(sync_client: pokelance.PokeLanceSyncClient) -> None:
    ping = sync_client.ping()
    assert ping >= 0, "Ping value must be non-negative."


# ---------------------------------------------------------------------------
# getch_data happy paths
# ---------------------------------------------------------------------------


def test_sync_getch_data_by_id(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon: Pokemon = sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    assert pokemon.name == "bulbasaur"


def test_sync_getch_data_by_name(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon: Pokemon = sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "bulbasaur")
    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "bulbasaur"


def test_sync_getch_data_cache_hit(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """Second call must return the exact same model instance from cache."""
    result1: Pokemon = sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    result2: Pokemon = sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    assert result1 == result2


def test_sync_getch_data_random_endpoint(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    """Fetch a random name from the endpoint registry; confirm it lands in cache."""
    id_ = random.choice(list(sync_cached_client.pokemon.cache_group.pokemon.endpoints.keys()))
    pokemon: Pokemon = sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", id_)
    assert pokemon.name == id_
    route = Endpoint.get_pokemon(id_)
    cached: Pokemon | None = sync_cached_client.pokemon.cache_group.pokemon.get(route)
    assert cached is not None and cached.name == id_


# ---------------------------------------------------------------------------
# getch_data error paths
# ---------------------------------------------------------------------------


def test_sync_getch_data_invalid_resource(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ResourceNotFound):
        sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "does-not-exist-zzz")


def test_sync_getch_data_invalid_category(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ValueError):
        sync_cached_client.getch_data(ExtensionEnum.Pokemon, "not-a-real-category", "bulbasaur")


def test_sync_getch_data_invalid_extension(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ValueError):
        sync_cached_client.getch_data("NotAnExtension", "pokemon", "bulbasaur")


# ---------------------------------------------------------------------------
# from_url happy path
# ---------------------------------------------------------------------------


def test_sync_from_url(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    id_ = random.choice(list(sync_cached_client.pokemon.cache_group.pokemon.endpoints.keys()))
    pokemon: Pokemon = sync_cached_client.from_url(f"https://pokeapi.co/api/v2/pokemon/{id_}")
    assert pokemon.name == id_
    route = Endpoint.get_pokemon(id_)
    cached: Pokemon | None = sync_cached_client.pokemon.cache_group.pokemon.get(route)
    assert cached is not None and cached.name == id_


# ---------------------------------------------------------------------------
# from_url error paths
# ---------------------------------------------------------------------------


def test_sync_from_url_invalid_resource(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ResourceNotFound):
        sync_cached_client.from_url("https://pokeapi.co/api/v2/pokemon/does-not-exist-zzz")


def test_sync_from_url_invalid_category(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ValueError):
        sync_cached_client.from_url("https://pokeapi.co/api/v2/garbage/something")


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------


def test_sync_get_image_returns_bytes(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.sprites.front_default is not None
    img = sync_cached_client.get_image(pokemon.sprites.front_default)
    assert img and isinstance(img, bytes)


def test_sync_get_image_cache_hit_is_faster(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    url = pokemon.sprites.front_default
    assert url is not None
    t0 = time.perf_counter()
    sync_cached_client.get_image(url)
    first = time.perf_counter() - t0
    t1 = time.perf_counter()
    sync_cached_client.get_image(url)
    second = time.perf_counter() - t1
    assert first > second, "Cached image fetch should be faster than the initial network fetch."


def test_sync_get_image_invalid_url(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ImageNotFound):
        sync_cached_client.get_image("https://pokeapi.co/api/v2/pokemon/invalid")


def test_sync_get_audio_returns_bytes(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.cries.latest is not None
    audio = sync_cached_client.get_audio(pokemon.cries.latest)
    assert audio and isinstance(audio, bytes)


def test_sync_get_audio_cache_hit_is_faster(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    url = pokemon.cries.latest
    assert url is not None
    t0 = time.perf_counter()
    sync_cached_client.get_audio(url)
    first = time.perf_counter() - t0
    t1 = time.perf_counter()
    sync_cached_client.get_audio(url)
    second = time.perf_counter() - t1
    assert first > second, "Cached audio fetch should be faster than the initial network fetch."


# ---------------------------------------------------------------------------
# Model equality & env vars
# ---------------------------------------------------------------------------


def test_sync_model_equality(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    p1 = sync_cached_client.pokemon.fetch_pokemon(1)
    p2 = sync_cached_client.pokemon.fetch_pokemon(1)
    assert p1 == p2


def test_sync_base_url_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    staging_url = "https://staging.pokeapi.co/api/v2"

    assert get_base_url() == DEFAULT_BASE_URL

    monkeypatch.setenv("POKEAPI_BASE_URL", staging_url)

    assert get_base_url() == staging_url

    with pokelance.PokeLanceSyncClient(cache_endpoints=False) as client:
        berry = client.berry.fetch_berry(1)

        assert berry.item.url.startswith(staging_url)
        assert berry.name == "cheri"


# ---------------------------------------------------------------------------
# Lifecycle and State
# ---------------------------------------------------------------------------


def test_sync_client_context_manager() -> None:
    client = pokelance.PokeLanceSyncClient(cache_endpoints=False)
    with client as c:
        assert c.http is not None
        assert c.pokemon is not None


def test_sync_client_manual_close() -> None:
    client = pokelance.PokeLanceSyncClient(cache_endpoints=False)
    berry = client.berry.fetch_berry(1)
    assert berry.name == "cheri"
    client.close()
    assert client.http.session is None
