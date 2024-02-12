import pytest

import pokelance


@pytest.mark.asyncio
async def test_cache_attributes(client: pokelance.PokeLance) -> None:
    assert client.http.cache.max_size == 100, "Default cache size is not 100."
    client.http.cache.set_size(255)
    assert client.http.cache.max_size == 255, "Cache size is not 255."
    client.http.cache.pokemon.set_size(100)
    assert client.http.cache.pokemon.max_size == 100, "Pokemon cache size is not 100."
    assert client.http.cache.client == client, "Client is not the same."


@pytest.mark.asyncio
async def test_cache(client: pokelance.PokeLance) -> None:
    client.http.cache.set_size(10)
    await client.pokemon.fetch_pokemon(1)
    assert len(client.http.cache.pokemon.pokemon.cache) == 1, "Pokemon cache is not 1."
    for i in range(2, 11):
        await client.pokemon.fetch_pokemon(i)
    assert len(client.http.cache.pokemon.pokemon.cache) == 10, "Pokemon cache is not 10."
    mon = await client.pokemon.fetch_pokemon(25)
    cache = client.http.cache.pokemon.pokemon.cache
    latest = cache[list(cache.keys())[-1]]
    assert mon == latest, "Pokemon is not the latest."


@pytest.mark.asyncio
async def test_endpoints_cache(client: pokelance.PokeLance) -> None:
    await client.pokemon.setup()  # internal method to load endpoints usually called based on param `cache_endpoints`
    assert len(client.http.cache.pokemon.pokemon.endpoints) > 0, "Pokemon cache is empty."
    assert len(client.http.cache.pokemon.pokemon_species.endpoints) > 0, "Pokemon species cache is empty."


@pytest.mark.asyncio
async def test_auto_cache(client: pokelance.PokeLance) -> None:
    await client.wait_until_ready()  # should fail since `cache_endpoints` is False
    await client.berry.setup()  # internal method to load endpoints usually called based on param `cache_endpoints`
    assert len(client.http.cache.berry.berry.endpoints) > 0, "Pokemon cache is empty."
    await client.berry.cache.berry_flavor.load_all()  # load all berry flavors
    assert len((c := client.http.cache.berry.berry_flavor).endpoints) == len(c), "Berry flavor cache is not full."


@pytest.mark.asyncio
async def test_image_cache(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    await client.get_image_async(pokemon.sprites.front_default)
    assert client.get_image_async.__contains__(client, pokemon.sprites.front_default), "Image is not in cache."
    client.get_image_async.cache_clear()
    assert (
        client.get_image_async.__contains__(client, pokemon.sprites.front_default) is False
    ), "Image is still in cache."
    client.get_image_async.set_size(10)
    assert client.get_image_async.cache_info().maxsize == 10, "Image cache size is not 10."


@pytest.mark.asyncio
async def test_audio_cache(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    await client.get_audio_async(pokemon.cries.latest)
    assert client.get_audio_async.__contains__(client, pokemon.cries.latest), "Audio is not in cache."
    client.get_audio_async.cache_clear()
    assert client.get_audio_async.__contains__(client, pokemon.cries.latest) is False, "Audio is still in cache."
    client.get_audio_async.set_size(10)
    assert client.get_audio_async.cache_info().maxsize == 10, "Audio cache size is not 10."
