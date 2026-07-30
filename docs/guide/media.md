# Media: Sprites & Cries

Pokémon models come back from PokéAPI full of URLs to sprites and cries, not the raw bytes.
PokeLance gives you two async helpers to fetch those, each backed by their own async LRU
cache so re-downloading the same sprite is instant. This page also shows both rendered
inline, live: the bytes are downloaded at doc-build time, base64-encoded, and dropped
straight into an `<img>`/`<audio>` tag.

## Fetching an image

[`get_image_async`][pokelance.client.PokeLance.get_image_async] downloads and validates any
sprite URL, returning raw `bytes`:

```python exec="true" source="above" result="text" session="media"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    img = await client.get_image_async(pokemon.sprites.front_default)
    await client.close()
    return f"downloaded {len(img)} bytes from {pokemon.sprites.front_default}"


print(asyncio.run(main()))
```

Accepted content types are `png`, `jpg`, `jpeg`, `gif`, `webp`, and `svg`, anything else
(or a non-2xx response) raises [`ImageNotFound`][pokelance.exceptions.ImageNotFound].

### Embedding it as `<img>`

```python exec="true" source="above" html="true" session="media"
import asyncio
import base64
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    img = await client.get_image_async(pokemon.sprites.front_default)
    await client.close()
    encoded = base64.b64encode(img).decode("ascii")
    return f'<img src="data:image/png;base64,{encoded}" alt="pikachu sprite" width="96" height="96"/>'


print(asyncio.run(main()))
```

## Fetching a cry

[`get_audio_async`][pokelance.client.PokeLance.get_audio_async] works identically, for the
newer `cries` field on [`Pokemon`][pokelance.models.abstract.pokemon.Pokemon] models:

```python exec="true" source="above" result="text" session="media"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    audio = await client.get_audio_async(pokemon.cries.latest)
    await client.close()
    return f"downloaded {len(audio)} bytes from {pokemon.cries.latest}"


print(asyncio.run(main()))
```

Accepted content types here are `ogg`, `wav`, and `mp3`; anything else raises
[`AudioNotFound`][pokelance.exceptions.AudioNotFound].

### Embedding it as `<audio>`

```python exec="true" source="above" html="true" session="media"
import asyncio
import base64
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    audio = await client.get_audio_async(pokemon.cries.latest)
    await client.close()
    encoded = base64.b64encode(audio).decode("ascii")
    return (
        f'<audio controls preload="none">'
        f'<source src="data:audio/ogg;base64,{encoded}" type="audio/ogg"></audio>'
    )


print(asyncio.run(main()))
```

## Why these are cached separately

Unlike model caches (bounded by `cache_size`), image and audio helpers are decorated with
PokeLance's own [`alru_cache`](../api_reference/utils.md), an async-aware LRU cache that
also de-duplicates concurrent in-flight requests for the same URL (two coroutines awaiting
the same sprite at the same time share one download instead of firing two).

Sizes are configured independently from the model cache, via the client constructor or
properties (see [Configuration](configuration.md#cache-sizing)):

```python
client = PokeLance(image_cache_size=256, audio_cache_size=64)
client.image_cache_size = 512  # can also be changed after construction
```

A cached hit is measurably faster since it skips the network entirely:

```python exec="true" source="above" result="text"
import asyncio
import time

from pokelance import PokeLance


async def main() -> None:
    client = PokeLance()
    url = (await client.pokemon.fetch_pokemon("pikachu")).sprites.front_default

    t0 = time.perf_counter()
    await client.get_image_async(url)
    first = time.perf_counter() - t0

    t1 = time.perf_counter()
    await client.get_image_async(url)  # same URL: served from the LRU cache
    second = time.perf_counter() - t1

    print(f"first fetch: {first:.4f}s, second fetch: {second:.4f}s")
    assert first > second
    await client.close()


asyncio.run(main())
```

## Error handling

Both helpers raise before returning any bytes if the response isn't actually image/audio
content, or the request failed outright:

```python exec="true" source="above" result="text" session="media"
import asyncio
from pokelance import PokeLance
from pokelance.exceptions import ImageNotFound

client = PokeLance()


async def main() -> None:
    try:
        await client.get_image_async("https://pokeapi.co/api/v2/pokemon/invalid")
    except ImageNotFound as exc:
        print(exc)  # e.g. "... was unsuccessful or the URL is not an image. (...) | ... | 404"
    finally:
        await client.close()

asyncio.run(main())
```

See [Error Handling](error_handling.md) for the full exception hierarchy.
