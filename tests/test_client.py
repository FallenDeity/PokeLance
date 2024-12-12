import random
import time
import typing as t

import pytest

import pokelance
from pokelance.cache import BaseCache
from pokelance.constants import ExtensionEnum
from pokelance.exceptions import ImageNotFound, ResourceNotFound
from pokelance.http import Endpoint
from pokelance.models import Pokemon


@pytest.mark.asyncio
async def test_client_ping(client: pokelance.PokeLance) -> None:
    ping_value = await client.ping()
    assert ping_value >= 0, "Ping value is negative."


@pytest.mark.asyncio
async def test_endpoint_cache(cached_client: pokelance.PokeLance) -> None:
    await cached_client.wait_until_ready()
    exts = [e.value for e in ExtensionEnum]
    for ext in exts:
        for category in ext.categories:
            cat = category.replace("-", "_")
            attr: BaseCache[t.Any, t.Any] = getattr(getattr(cached_client, f"{ext.name}").cache, cat)
            assert attr.endpoints, f"Endpoint cache for {category} in {ext.name} is empty."


@pytest.mark.asyncio
async def test_getch_data(cached_client: pokelance.PokeLance) -> None:
    _id = random.choice(list(cached_client.pokemon.cache.pokemon.endpoints.keys()))
    pokemon: Pokemon = await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", _id)
    assert pokemon.name == _id, "Pokemon not fetched."
    route = Endpoint.get_pokemon(_id)
    _cached_pokemon: t.Optional[Pokemon] = cached_client.pokemon.cache.pokemon.get(route)
    assert _cached_pokemon and _cached_pokemon.name == _id, "Pokemon not cached."


@pytest.mark.asyncio
async def test_getch_data_invalid(cached_client: pokelance.PokeLance) -> None:
    with pytest.raises(ResourceNotFound):
        await cached_client.getch_data(ExtensionEnum.Pokemon, "pokemon", "invalid")
    with pytest.raises(ValueError):
        await cached_client.getch_data(ExtensionEnum.Pokemon, "invalid", "invalid")
    with pytest.raises(ValueError):
        await cached_client.getch_data("invalid", "invalid", "invalid")


@pytest.mark.asyncio
async def test_from_url(cached_client: pokelance.PokeLance) -> None:
    _id = random.choice(list(cached_client.pokemon.cache.pokemon.endpoints.keys()))
    pokemon: Pokemon = await cached_client.from_url(f"https://pokeapi.co/api/v2/pokemon/{_id}")
    assert pokemon.name == _id, "Pokemon not fetched."
    route = Endpoint.get_pokemon(_id)
    _cached_pokemon: t.Optional[Pokemon] = cached_client.pokemon.cache.pokemon.get(route)
    assert _cached_pokemon and _cached_pokemon.name == _id, "Pokemon not cached."


@pytest.mark.asyncio
async def test_from_url_invalid(cached_client: pokelance.PokeLance) -> None:
    with pytest.raises(ResourceNotFound):
        await cached_client.from_url("https://pokeapi.co/api/v2/pokemon/invalid")
    with pytest.raises(ValueError):
        await cached_client.from_url("https://pokeapi.co/api/v2/garbage/invalid")


@pytest.mark.asyncio
async def test_get_image(cached_client: pokelance.PokeLance) -> None:
    pokemon = await cached_client.pokemon.fetch_pokemon(1)
    start = time.perf_counter()
    img = await cached_client.get_image_async(pokemon.sprites.front_default)
    end = time.perf_counter()
    await cached_client.get_image_async(pokemon.sprites.front_default)
    final = time.perf_counter()
    assert end - start > final - end, "Image was not cached."
    assert img and isinstance(img, bytes), "Image is not bytes."


@pytest.mark.asyncio
async def test_get_image_invalid(cached_client: pokelance.PokeLance) -> None:
    with pytest.raises(ImageNotFound):
        await cached_client.get_image_async("https://pokeapi.co/api/v2/pokemon/invalid")


@pytest.mark.asyncio
async def test_model_equality(cached_client: pokelance.PokeLance) -> None:
    pokemon_1 = await cached_client.pokemon.fetch_pokemon(1)
    pokemon_2 = await cached_client.pokemon.fetch_pokemon(1)
    assert pokemon_1 == pokemon_2, "Pokemon models are not equal."
