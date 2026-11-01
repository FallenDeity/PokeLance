"""
Tests for the top-level PokeLance sync client helpers.

Coverage
--------
- ping / latency sanity check
- getch_data: happy paths (int id, string name, random endpoint, cache-hit)
- getch_data: error paths (invalid resource, category, extension)
- from_url: happy path + error paths
- get_image / get_audio: bytes returned, cache hits, errors
- base_url env var support
"""

from __future__ import annotations

import random
import threading
from unittest.mock import Mock

import niquests
import pytest

import pokelance
from pokelance.constants import DEFAULT_BASE_URL, ExtensionEnum, get_base_url
from pokelance.endpoints import Endpoint, Route
from pokelance.exceptions import HTTPException, ImageNotFound, ResourceNotFound
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
    assert isinstance(pokemon, Pokemon) and pokemon.name == "bulbasaur"
    assert sync_cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "bulbasaur") is pokemon


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


@pytest.mark.parametrize(
    ("path", "endpoint"),
    [
        ("pokemon/25/", "/pokemon/25"),
        ("pokemon/pikachu/encounters/", "/pokemon/pikachu/encounters"),
        ("meta/", "/meta"),
    ],
)
def test_sync_from_url_preserves_valid_paths(
    sync_client: pokelance.PokeLanceSyncClient, monkeypatch: pytest.MonkeyPatch, path: str, endpoint: str
) -> None:
    request = Mock(return_value=[] if endpoint.endswith("/encounters") else {})
    monkeypatch.setattr(sync_client.http, "request", request)
    sync_client.from_url(f"https://pokeapi.co/api/v2/{path}")
    assert request.call_args.args[0].endpoint == endpoint


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------


def test_sync_get_image_returns_bytes(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.sprites.front_default is not None
    img = sync_cached_client.get_image(pokemon.sprites.front_default)
    assert img and isinstance(img, bytes)
    hits = sync_cached_client._cached_get_image.cache_info().hits
    assert sync_cached_client.get_image(pokemon.sprites.front_default) is img
    assert sync_cached_client._cached_get_image.cache_info().hits == hits + 1


def test_sync_get_image_invalid_url(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    with pytest.raises(ImageNotFound):
        sync_cached_client.get_image("https://pokeapi.co/api/v2/pokemon/invalid")


def test_sync_get_audio_returns_bytes(sync_cached_client: pokelance.PokeLanceSyncClient) -> None:
    pokemon = sync_cached_client.pokemon.fetch_pokemon(1)
    assert pokemon.cries.latest is not None
    audio = sync_cached_client.get_audio(pokemon.cries.latest)
    assert audio and isinstance(audio, bytes)
    hits = sync_cached_client._cached_get_audio.cache_info().hits
    assert sync_cached_client.get_audio(pokemon.cries.latest) is audio
    assert sync_cached_client._cached_get_audio.cache_info().hits == hits + 1


def test_sync_media_transport_error_is_wrapped() -> None:
    url = "https://media.example/asset"
    transport_error = niquests.exceptions.RequestException("transport failed")
    session = Mock(request=Mock(side_effect=transport_error))
    client = pokelance.PokeLanceSyncClient(cache_endpoints=False, session=session, setup_logging=False)

    try:
        with pytest.raises(HTTPException) as exc_info:
            client.http.load_image(url)
    finally:
        client.close()

    assert exc_info.value.__cause__ is transport_error
    assert exc_info.value.route.url == url
    assert exc_info.value.status == -1


# ---------------------------------------------------------------------------
# Base URL configuration
# ---------------------------------------------------------------------------


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


def test_sync_fetch_refreshes_cache(
    sync_client: pokelance.PokeLanceSyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = Mock(side_effect=[{"name": "old"}, {"name": "new"}, RuntimeError("request failed")])
    monkeypatch.setattr(sync_client.http, "request", request)
    first = sync_client.berry.fetch_berry(1)
    second = sync_client.berry.fetch_berry(1)
    assert second is not first and second.name == "new"
    assert sync_client.berry.get_berry(1) is second
    assert request.call_count == 2
    with pytest.raises(RuntimeError, match="request failed"):
        sync_client.berry.fetch_berry(1)
    assert sync_client.berry.get_berry(1) is second


def test_sync_close_waits_for_endpoint_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    factory = Mock(return_value=session)
    monkeypatch.setattr("pokelance.http._sync.niquests.Session", factory)
    client = pokelance.PokeLanceSyncClient(setup_logging=False)
    started, release, shutting_down, rejected = (threading.Event() for _ in range(4))

    def worker() -> None:
        started.set()
        assert release.wait(5)
        try:
            client.http.request(Route())
        except RuntimeError:
            rejected.set()

    shutdown = client.http.loader.shutdown

    def observed_shutdown() -> None:
        shutting_down.set()
        shutdown()

    monkeypatch.setattr(client.http.loader, "shutdown", observed_shutdown)
    client.ext_tasks.clear()
    client.ext_tasks.append((worker, "test"))
    client.http.connect()
    closer = threading.Thread(target=client.close)
    try:
        assert started.wait(2)
        closer.start()
        assert shutting_down.wait(2)
        closer.join(timeout=0.05)
        assert closer.is_alive(), "close() must wait for the running worker"
        session.close.assert_not_called()
    finally:
        release.set()
        if closer.ident is not None:
            closer.join(timeout=3)
        client.close()

    assert not closer.is_alive(), "Worker shutdown must not deadlock"
    assert rejected.is_set()
    assert not client.http.is_connected
    assert client.http.loader.is_ready
    assert factory.call_count == 1
    session.request.assert_not_called()
    session.close.assert_called_once()
