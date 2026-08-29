# Media: Sprites & Cries

Pokémon models come back from PokéAPI full of URLs to sprites and cries, not raw bytes. PokeLance provides dedicated helpers (`get_image` and `get_audio`) to fetch those, backed by an LRU cache so repeated lookups are instant.

## Fetching an image

[`get_image`][pokelance.client.async_client.PokeLanceAsyncClient.get_image] downloads and validates any sprite URL, returning raw `bytes`:

=== "Async"

    ```python exec="true" source="above" result="text" session="media_img_async"
    import asyncio
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            pokemon = await client.pokemon.fetch_pokemon("pikachu")
            assert pokemon.sprites.front_default is not None
            img = await client.get_image(pokemon.sprites.front_default)
            print(f"Downloaded {len(img)} bytes from {pokemon.sprites.front_default}")


    asyncio.run(main())
    ```

=== "Sync"

    ```python exec="true" source="above" result="text" session="media_img_sync"
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        pokemon = client.pokemon.fetch_pokemon("pikachu")
        assert pokemon.sprites.front_default is not None
        img = client.get_image(pokemon.sprites.front_default)
        print(f"Downloaded {len(img)} bytes from {pokemon.sprites.front_default}")
    ```

Accepted content types are `png`, `jpg`, `jpeg`, `gif`, `webp`, and `svg`; anything else raises [`ImageNotFound`][pokelance.exceptions.ImageNotFound].

```python exec="true" source="above" html="true" session="media_img_async"
import asyncio
import base64
from pokelance import PokeLanceAsyncClient


async def main() -> str:
    async with PokeLanceAsyncClient() as client:
        pokemon = await client.pokemon.fetch_pokemon("pikachu")
        assert pokemon.sprites.front_default is not None
        img = await client.get_image(pokemon.sprites.front_default)
        encoded = base64.b64encode(img).decode("ascii")
        return f'<img src="data:image/png;base64,{encoded}" alt="pikachu sprite" width="96" height="96"/>'


print(asyncio.run(main()))
```

## Fetching a cry

[`get_audio`][pokelance.client.async_client.PokeLanceAsyncClient.get_audio] works identically for the `cries` field on [`Pokemon`][pokelance.models.abstract.pokemon.Pokemon] models:

=== "Async"

    ```python exec="true" source="above" result="text" session="media_cry_async"
    import asyncio
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            pokemon = await client.pokemon.fetch_pokemon("pikachu")
            audio = await client.get_audio(pokemon.cries.latest)
            print(f"Downloaded {len(audio)} bytes from {pokemon.cries.latest}")


    asyncio.run(main())
    ```

=== "Sync"

    ```python exec="true" source="above" result="text" session="media_cry_sync"
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        pokemon = client.pokemon.fetch_pokemon("pikachu")
        audio = client.get_audio(pokemon.cries.latest)
        print(f"Downloaded {len(audio)} bytes from {pokemon.cries.latest}")
    ```

Accepted content types are `ogg`, `wav`, and `mp3`; anything else raises [`AudioNotFound`][pokelance.exceptions.AudioNotFound].

```python exec="true" source="above" html="true" session="media_cry_async"
import asyncio
import base64
from pokelance import PokeLanceAsyncClient


async def main() -> str:
    async with PokeLanceAsyncClient() as client:
        pokemon = await client.pokemon.fetch_pokemon("pikachu")
        audio = await client.get_audio(pokemon.cries.latest)
        encoded = base64.b64encode(audio).decode("ascii")
        return (
            f'<audio controls preload="none">'
            f'<source src="data:audio/ogg;base64,{encoded}" type="audio/ogg"></audio>'
        )


print(asyncio.run(main()))
```

## Media caching

Image and audio helpers in `PokeLanceAsyncClient` use an asynchronous LRU cache (`alru_cache`), which deduplicates concurrent in-flight requests for the same URL.

Cache sizes can be configured during client construction or dynamically:

```python
client = PokeLanceAsyncClient(image_cache_size=256, audio_cache_size=64)
client.image_cache_size = 512  # resize image cache
```

## Error handling

Both helpers raise descriptive exceptions if the media URL is invalid or the network request fails:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient
from pokelance.exceptions import ImageNotFound


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        try:
            await client.get_image("https://pokeapi.co/api/v2/pokemon/invalid")
        except ImageNotFound as exc:
            print(f"Caught expected error: {exc}")


asyncio.run(main())
```

See [Error Handling](error_handling.md) for the full exception hierarchy.
