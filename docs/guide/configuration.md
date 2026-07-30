# Configuration

[`PokeLance`][pokelance.client.PokeLance] accepts a handful of keyword-only arguments that control
caching, logging, and session ownership. All of them have sane defaults, so `PokeLance()`
with no arguments is a perfectly valid client.

```python
client = PokeLance(
    audio_cache_size=128,
    image_cache_size=128,
    cache_size=100,
    logger=None,
    file_logging=False,
    cache_endpoints=True,
    session=None,
)
```

| Parameter          | Type                              | Default | Purpose                                                                                                     |
| ------------------ | --------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `cache_size`       | `int`                             | `100`   | Max entries kept per-resource-type in the LRU model cache (see [Caching](caching.md)).                      |
| `image_cache_size` | `int`                             | `128`   | Max entries in the async LRU cache backing [`get_image_async`][pokelance.client.PokeLance.get_image_async]. |
| `audio_cache_size` | `int`                             | `128`   | Max entries in the async LRU cache backing [`get_audio_async`][pokelance.client.PokeLance.get_audio_async]. |
| `cache_endpoints`  | `bool`                            | `True`  | Whether to eagerly cache the *name/id registries* for every extension on startup.                           |
| `session`          | `Optional[aiohttp.ClientSession]` | `None`  | Bring your own session; otherwise one is lazily created and owned by the client.                            |
| `logger`           | `Optional[logging.Logger]`        | `None`  | Provide your own logger; otherwise PokeLance's own [`Logger`][pokelance.logger.Logger] is used.             |
| `file_logging`     | `bool`                            | `False` | When using the built-in logger, also write timestamped log files under `logs/`.                             |

## Cache sizing

Every extension (`berry`, `pokemon`, `move`, ...) gets its own set of per-category LRU
caches sized by `cache_size`. Bump this up if you're iterating over large swaths of the
Pokédex and don't want to keep re-fetching:

```python
from pokelance import PokeLance

client = PokeLance(cache_size=1000)  # keep up to 1000 of *each* resource category
```

You can also resize a running client's caches (this re-applies the limit to every
sub-cache):

```python
client.http.cache.set_size(500)
```

Image and audio caches are independent since they store raw `bytes` rather than models, and
resizing them is exposed directly on the client:

```python
client.image_cache_size = 256
client.audio_cache_size = 32
```

## Disabling endpoint pre-loading

By default (`cache_endpoints=True`), as soon as the client connects it schedules background
tasks that fetch every extension's *list* endpoints (e.g. `GET /pokemon?limit=10000`) so
that `get_*`/`fetch_*` calls can validate names/ids and suggest corrections immediately.

If you only ever fetch a handful of known resources and want to skip that warm-up entirely
(useful in tests, or serverless functions with a cold-start budget), disable it:

```python
client = PokeLance(cache_endpoints=False)
```

!!! warning "Effect on validation"
    With `cache_endpoints=False`, [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound]
    suggestions won't be available (the registries they're computed from are empty), but
    fetching still works exactly the same, a request is simply sent straight to the
    API and any 404 still raises normally.

## Waiting for the registries to finish loading

Pre-loading happens in the background via `asyncio.create_task`, so it doesn't block your
first request. If you need to *guarantee* the registries are fully populated (for example,
before iterating `client.pokemon.all_pokemons`), await
[`wait_until_ready()`][pokelance.client.PokeLance.wait_until_ready]:

```python
import asyncio
from pokelance import PokeLance


async def main() -> None:
    client = PokeLance()
    await client.wait_until_ready()
    print(len(client.pokemon.all_pokemons or []))
    await client.close()


asyncio.run(main())
```

## Bringing your own session

Useful when PokeLance shares an event loop and connection pool with something else that
also owns an `aiohttp.ClientSession`, a web app sharing one session across its request
lifespan being the canonical example (see the [FastAPI recipe](recipes/fastapi.md)):

```python
import aiohttp
from pokelance import PokeLance

session = aiohttp.ClientSession()
client = PokeLance(session=session)
```

PokeLance will *use* the session but won't close it on `client.close()` unless it created
it itself, closing `session` yourself remains your responsibility in that case.

## Logging

The default [`Logger`][pokelance.logger.Logger] is a colorized `logging.Logger` subclass.
Pass `file_logging=True` to also persist rotating, dated log files under `logs/<name>-<date>.log`:

```python
client = PokeLance(file_logging=True)
client.logger.info("This goes to both stdout and logs/pokelance-YYYY-MM-DD.log")
```

Prefer your own logging setup? Pass any standard `logging.Logger`:

```python
import logging
from pokelance import PokeLance

logger = logging.getLogger("my-app")
client = PokeLance(logger=logger)
```
