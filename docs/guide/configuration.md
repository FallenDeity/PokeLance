# Configuration

Both [`PokeLanceAsyncClient`][pokelance.client.async_client.PokeLanceAsyncClient] and [`PokeLanceSyncClient`][pokelance.client.sync_client.PokeLanceSyncClient] accept keyword arguments controlling cache sizing, logging, endpoint caching, and HTTP sessions. All options have sane defaults:

```python
from pokelance import PokeLanceAsyncClient

client = PokeLanceAsyncClient(
    cache_size=100,
    audio_cache_size=128,
    image_cache_size=128,
    cache_endpoints=True,
    setup_logging=True,
    file_logging=False,
    structured_logging=False,
    session=None,
)
```

| Parameter            | Type                                            | Default            | Purpose                                                                                           |
| -------------------- | ----------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------- |
| `cache_size`         | `int`                                           | `100`              | Max entries kept per-category in the LRU model cache (see [Caching](caching.md)).                |
| `image_cache_size`   | `int`                                           | `128`              | Max entries in the LRU cache backing [`get_image`][pokelance.client.async_client.PokeLanceAsyncClient.get_image].   |
| `audio_cache_size`   | `int`                                           | `128`              | Max entries in the LRU cache backing [`get_audio`][pokelance.client.async_client.PokeLanceAsyncClient.get_audio].   |
| `cache_endpoints`    | `bool`                                          | `True`             | Whether to eagerly cache name/id registries on client startup for fuzzy search & validation.       |
| `setup_logging`      | `bool`                                          | `True`             | Whether PokeLance should configure default terminal logging.                                     |
| `log_level`          | `int`                                           | `logging.INFO`     | Log severity level filter.                                                                        |
| `file_logging`       | `bool`                                          | `False`            | Whether to write timestamped log files under `log_dir`.                                           |
| `structured_logging` | `bool`                                          | `False`            | Output logs as structured JSON rather than ANSI-colored plain text.                              |
| `log_dir`            | `str \| Path`                                   | `"logs/"`          | Directory destination when `file_logging=True`.                                                   |
| `session`            | `niquests.AsyncSession \| niquests.Session \| None` | `None`          | Optional external niquests session instance.                                                      |

## Cache sizing

Every resource category (`pokemon`, `berry`, `move`, ...) gets its own LRU cache sized by `cache_size`:

```python
from pokelance import PokeLanceAsyncClient

client = PokeLanceAsyncClient(cache_size=1000)  # keep up to 1000 of *each* resource category
```

You can also resize a running client's caches dynamically:

```python
client.http.cache_manager.set_size(500)
```

Image and audio caches are independent since they store raw `bytes` rather than model objects:

```python
client.image_cache_size = 256
client.audio_cache_size = 32
```

## Disabling endpoint pre-loading

By default (`cache_endpoints=True`), when the client initializes, it schedules background tasks that fetch every extension's list index (e.g. `GET /pokemon?limit=10000`) so that `get_*`/`fetch_*` calls can validate names/ids and suggest fuzzy corrections immediately.

If you only ever fetch a handful of known resources and want to skip that warm-up entirely:

```python
client = PokeLanceAsyncClient(cache_endpoints=False)
```

!!! warning "Effect on validation"
    With `cache_endpoints=False`, [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound]
    suggestions won't be available, but fetching still works as requests are dispatched directly to the API.

## Waiting for registries to finish loading

Pre-loading happens asynchronously in the background. If you need to *guarantee* registries are fully loaded before querying (e.g. before iterating known identifiers):

=== "Async"

    ```python exec="true" source="above" result="text"
    import asyncio
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            await client.wait_until_ready()
            pokemon_names = client.pokemon.cache_group.pokemon.identifiers
            print(f"Registered {len(pokemon_names)} Pokemon names/IDs")


    asyncio.run(main())
    ```

=== "Sync"

    ```python exec="true" source="above" result="text"
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        client.wait_until_ready()
        pokemon_names = client.pokemon.cache_group.pokemon.identifiers
        print(f"Registered {len(pokemon_names)} Pokemon names/IDs")
    ```

## Bringing your own session

When PokeLance shares an HTTP session with another service (such as in a FastAPI app):

=== "Async"

    ```python
    import asyncio
    import niquests
    from pokelance import PokeLanceAsyncClient


    async def main() -> None:
        async with niquests.AsyncSession() as session:
            async with PokeLanceAsyncClient(session=session) as client:
                pokemon = await client.pokemon.fetch_pokemon("pikachu")
                print(pokemon.name)


    asyncio.run(main())
    ```

=== "Sync"

    ```python
    import niquests
    from pokelance import PokeLanceSyncClient

    with niquests.Session() as session:
        with PokeLanceSyncClient(session=session) as client:
            pokemon = client.pokemon.fetch_pokemon("pikachu")
            print(pokemon.name)
    ```

PokeLance will use the shared session without closing it when the client exits.

## Logging

PokeLance comes with built-in colorized logging and structured JSON formatting:

```python
from pokelance import PokeLanceAsyncClient

# Enable structured JSON logging with file outputs
client = PokeLanceAsyncClient(
    structured_logging=True,
    file_logging=True,
    log_dir="logs/",
)
```
