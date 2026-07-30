---
title: Quickstart
---

# Quickstart

This tutorial will walk you through the basics of using PokeLance, from setting up a client understanding it's lifecycle to fetching resources from the PokéAPI.

## Creating a client

The simplest possible client needs no arguments at all:

```python exec="true" source="above" result="text" session="quickstart"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    print(await client.ping())
    await client.close()  # always call close() when you're done with a client to free up resources


asyncio.run(main())
```

`PokeLance()` lazily creates its own `aiohttp.ClientSession` on the first request. That's
convenient for quick scripts, but for anything long-lived (bots, web servers) prefer the
async context manager below so the session is guaranteed to close.

### With an async context manager

=== "Recommended"

    ```python
    import asyncio
    import aiohttp
    from pokelance import PokeLance


    async def main() -> None:
        async with aiohttp.ClientSession() as session, PokeLance(session=session) as client:
            print(await client.ping())
            berry = await client.berry.fetch_berry("cheri")
            print(berry.name)
        # session and client are both closed here automatically


    asyncio.run(main())
    ```

=== "Client-owned session"

    ```python
    import asyncio
    from pokelance import PokeLance


    async def main() -> None:
        async with PokeLance() as client:
            print(await client.ping())
            berry = await client.berry.fetch_berry("cheri")
            print(berry.name)


    asyncio.run(main())
    ```

!!! note "More on Async Context Managers"
    To learn more about async context managers and why they are useful, refer to this article: [Async Context Managers in Python](https://bbc.github.io/cloudfit-public-docs/asyncio/asyncio-part-3.html).

!!! tip "Bring your own session"
    Passing your own `aiohttp.ClientSession` is useful when PokeLance is one HTTP client
    among several in your app (e.g. another API client, or an internal service). It allows you to share the same session and connection pool across multiple clients, which can improve performance and resource usage.

## Fetching a few resources

This example hits the `https://pokeapi.co/api/v2/` endpoint to fetch a berry, its flavor, and its firmness:

```python exec="true" source="above" result="text" session="quickstart"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    latency = await client.ping()
    berry = await client.berry.fetch_berry("cheri")
    flavor = await client.berry.fetch_berry_flavor(berry.flavors[0].flavor.name)
    firmness = await client.berry.fetch_berry_firmness(berry.firmness.name)
    print(f"ping: {latency:.4f}s")
    print(f"berry: {berry.name} (id={berry.id}, growth_time={berry.growth_time})")
    print(f"flavor: {flavor.name}")
    print(f"firmness: {firmness.name}")
    await client.close()


asyncio.run(main())
```

!!! tip "Fully Typed Models"
    All models and each of their fields are fully typed with `attrs` so you can use your favorite IDE's autocomplete and type checking features to explore the API surface.

## Rendering a sprite inline

The client includes a convenience method for fetching related media resources (images and audio) present in PokéAPI with some additional guardrails to ensure the response is valid and also includes a simple caching layer to avoid repeated network requests for the same resource. This example fetches Pikachu's front sprite and renders it inline as a base64-encoded `<img>` tag:

```python exec="true" source="above" html="true" session="quickstart"
import asyncio
import base64
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    sprite = await client.get_image_async(pokemon.sprites.front_default)
    await client.close()
    encoded = base64.b64encode(sprite).decode("ascii")
    return (
        f'<img src="data:image/png;base64,{encoded}" '
        f'alt="{pokemon.name} sprite" width="96" height="96"/>'
    )


print(asyncio.run(main()))
```

See [Media](media.md) for the full breakdown of `get_image_async`/`get_audio_async`.

## Reading the response as a dict

Every model inherits `to_dict()` (see
[`BaseModel`][pokelance.models._base.BaseModel]), which recursively serializes attrs models
and enums back into plain Python data, handy for logging, inspecting the raw payload, or just
dumping it to JSON.

```python exec="true" source="above" result="json" session="quickstart"
import asyncio
import json
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    berry = await client.berry.fetch_berry("cheri")
    await client.close()
    return json.dumps(berry.to_dict(), indent=2, default=str)[:600] + "\n..."


print(asyncio.run(main()))
```

`berry.raw` is also always available if you need the exact untouched JSON PokéAPI sent
back, before any model parsing happened.

## Cache-then-fetch, by hand

Every resource has a synchronous `get_*` (cache-only) and an asynchronous `fetch_*`
(cache-or-network) counterpart. This is the idiom used throughout the whole library:

```python
print(client.berry.get_berry("cheri"))          # None on a cold cache
print(await client.berry.fetch_berry("cheri"))  # hits network, populates cache
print(client.berry.get_berry("cheri"))          # now cached, instant
```

See [Fetching Data](fetching_data.md) for the full rationale, and
[`getch_data`][pokelance.client.PokeLance.getch_data] for a single call that does both steps
for you across any extension.

## Next steps

- [Configuration](configuration.md): cache sizes, logging, endpoint pre-loading
- [Extensions Reference](extensions.md): the full map of what you can fetch
- [Caching In Depth](caching.md): persist entire resource sets to disk
