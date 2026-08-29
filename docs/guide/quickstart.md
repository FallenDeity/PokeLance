---
title: Quickstart
---

# Quickstart

This tutorial will walk you through the basics of using PokeLance, from setting up a client and understanding its lifecycle to fetching resources from the PokéAPI.

PokeLance supports both asynchronous (`PokeLanceAsyncClient`) and synchronous (`PokeLanceSyncClient`) paradigms out of the box.

## Creating a client

The simplest possible client needs no arguments at all:

=== "Async"

    ```python
    import asyncio
    from pokelance import PokeLanceAsyncClient

    client = PokeLanceAsyncClient()


    async def main() -> None:
        print(await client.ping())
        await client.close()  # always close the client when done to free resources


    asyncio.run(main())
    ```

=== "Sync"

    ```python
    from pokelance import PokeLanceSyncClient

    client = PokeLanceSyncClient()

    print(client.ping())
    client.close()
    ```

PokeLance lazily creates its own `niquests.AsyncSession` or `niquests.Session` on the first request. That's convenient for quick scripts, but for anything long-lived (bots, web servers) prefer context managers so the session is guaranteed to close cleanly.

### With a context manager

=== "Async Context Manager"

    ```python exec="true" source="above" result="text" session="qs_async"
    import asyncio
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            print(await client.ping())
            berry = await client.berry.fetch_berry("cheri")
            print(berry.name)
        # client and HTTP session are both closed here automatically


    asyncio.run(main())
    ```

=== "Sync Context Manager"

    ```python exec="true" source="above" result="text" session="qs_sync"
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        print(client.ping())
        berry = client.berry.fetch_berry("cheri")
        print(berry.name)
    # client and HTTP session are both closed here automatically
    ```

=== "Bring Your Own Session"

    ```python
    import asyncio
    import niquests
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with niquests.AsyncSession() as session, PokeLanceAsyncClient(session=session) as client:
            print(await client.ping())
            berry = await client.berry.fetch_berry("cheri")
            print(berry.name)


    asyncio.run(main())
    ```

!!! tip "Bring your own session"
    Passing your own `niquests.AsyncSession` or `niquests.Session` is useful when PokeLance shares a connection pool with other HTTP services in your app.

!!! note "More on Async Context Managers"
    If you're new to async context managers in Python, check out the [Python Documentation on Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers) and [`contextlib.asynccontextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager).

## Fetching a few resources

This example hits the PokéAPI endpoint to fetch a berry, its flavor, and its firmness:

=== "Async"

    ```python exec="true" source="above" result="text" session="qs_fetch_async"
    import asyncio
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            latency = await client.ping()
            berry = await client.berry.fetch_berry("cheri")
            flavor = await client.berry.fetch_berry_flavor(berry.flavors[0].flavor.name)
            firmness = await client.berry.fetch_berry_firmness(berry.firmness.name)
            print(f"ping: {latency:.4f}s")
            print(f"berry: {berry.name} (id={berry.id}, growth_time={berry.growth_time})")
            print(f"flavor: {flavor.name}")
            print(f"firmness: {firmness.name}")


    asyncio.run(main())
    ```

=== "Sync"

    ```python exec="true" source="above" result="text" session="qs_fetch_sync"
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        latency = client.ping()
        berry = client.berry.fetch_berry("cheri")
        flavor = client.berry.fetch_berry_flavor(berry.flavors[0].flavor.name)
        firmness = client.berry.fetch_berry_firmness(berry.firmness.name)
        print(f"ping: {latency:.4f}s")
        print(f"berry: {berry.name} (id={berry.id}, growth_time={berry.growth_time})")
        print(f"flavor: {flavor.name}")
        print(f"firmness: {firmness.name}")
    ```

!!! tip "Fully Typed Models"
    All models and each of their fields are fully typed with `attrs` and modern type annotations, providing accurate autocomplete and validation in IDEs, Pyright, and Ty.

## Fetching media resources

The client includes convenience methods (`get_image` and `get_audio`) for fetching media resources with built-in LRU caching:

```python exec="true" source="above" html="true" session="quickstart"
import asyncio
import base64
from pokelance import PokeLanceAsyncClient


async def main() -> str:
    async with PokeLanceAsyncClient() as client:
        pokemon = await client.pokemon.fetch_pokemon("pikachu")
        assert pokemon.sprites.front_default is not None
        sprite = await client.get_image(pokemon.sprites.front_default)
        encoded = base64.b64encode(sprite).decode("ascii")
        return f'<img src="data:image/png;base64,{encoded}" alt="{pokemon.name} sprite" width="96" height="96"/>'


print(asyncio.run(main()))
```

See [Media](media.md) for the full breakdown of `get_image` and `get_audio`.

## Reading the response as a dict

Every model inherits `to_dict()` (see [`BaseModel`][pokelance.models._base.BaseModel]), which recursively serializes attrs models and enums back into plain Python data:

```python exec="true" source="above" result="json" session="quickstart"
import asyncio
import json
from pokelance import PokeLanceAsyncClient


async def main() -> str:
    async with PokeLanceAsyncClient() as client:
        berry = await client.berry.fetch_berry("cheri")
        return json.dumps(berry.to_dict(), indent=2, default=str)[:600] + "\n..."


print(asyncio.run(main()))
```

`berry.raw` is also always available if you need the exact untouched JSON PokéAPI payload.

## Cache-then-fetch, by hand

Every resource category provides a cache lookup (`get_*`) and a network fetch (`fetch_*`) counterpart:

```python
# Synchronous cache check:
print(client.berry.get_berry("cheri"))  # None on cold cache

# Network fetch & cache population:
print(await client.berry.fetch_berry("cheri"))  # hits network, populates cache

# Subsequent cache check:
print(client.berry.get_berry("cheri"))  # cached, instant lookup
```

See [Fetching Data](fetching_data.md) for details, and [`getch_data`][pokelance.client.async_client.PokeLanceAsyncClient.getch_data] for a single call that performs cache-then-fetch across any extension.

## Configuring the API Base URL

By default, PokeLance connects to `https://pokeapi.co/api/v2/`. You can override this by setting the `POKEAPI_BASE_URL` environment variable:

```bash
export POKEAPI_BASE_URL=https://my-pokeapi-proxy.com/api/v2
```

## Next steps

- [Configuration](configuration.md): cache sizes, logging, endpoint pre-loading
- [Extensions Reference](extensions.md): the full map of what you can fetch
- [Caching In Depth](caching.md): in-memory LRU and disk cache persistence
