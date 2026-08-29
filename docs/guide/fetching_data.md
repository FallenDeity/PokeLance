# Fetching Data

PokeLance exposes every PokéAPI resource through a consistent, predictable pattern repeated across all 11 extensions and ~60 categories.

## The `get_*` / `fetch_*` pair

Every category (`berry`, `pokemon`, `move`, ...) provides two methods:

``` mermaid
flowchart LR
    A["client.berry.get_berry('cheri')"] -->|cache hit| B(Berry instance)
    A -->|cache miss| C[None]
    D["client.berry.fetch_berry('cheri')"] -->|cache hit| B
    D -->|cache miss| E[GET pokeapi.co/api/v2/berry/cheri] --> F[cache the result] --> B
```

- **`get_<category>(name_or_id)`**: Synchronous, cache-only. Returns the cached model or `None` if not cached yet. Never touches the network.
- **`fetch_<category>(name_or_id)`**: Cache-or-network. Returns the cached model if present, otherwise makes an HTTP request, caches the parsed model, and returns it. (Async in `PokeLanceAsyncClient`, Sync in `PokeLanceSyncClient`).

=== "Async"

    ```python
    berry = client.berry.get_berry("cheri")  # None the first time
    berry = await client.berry.fetch_berry("cheri")  # network request + cache
    berry = client.berry.get_berry("cheri")  # now cached, instant lookup
    ```

=== "Sync"

    ```python
    berry = client.berry.get_berry("cheri")  # None the first time
    berry = client.berry.fetch_berry("cheri")  # network request + cache
    berry = client.berry.get_berry("cheri")  # now cached, instant lookup
    ```

Both accept either the resource's **name** (`str`) or **id** (`int`) interchangeably:

```python
await client.pokemon.fetch_pokemon("bulbasaur")
await client.pokemon.fetch_pokemon(1)  # resolves to the same resource
```

## Validation and "did you mean...?"

Before touching the network, PokeLance checks the requested name/id against the extension's pre-loaded endpoint registry. If it isn't a known resource, a [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] exception is raised immediately with close-match suggestions:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient
from pokelance.exceptions import ResourceNotFound


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        await client.wait_until_ready()
        try:
            await client.berry.fetch_berry("chery")  # typo for "cheri"
        except ResourceNotFound as exc:
            print(f"Error: {exc}")
            print(f"Suggestions: {exc.suggestions}")  # ['cheri']


asyncio.run(main())
```

See [Error Handling](error_handling.md) for the full exception hierarchy.

## One call for any extension: `getch_data`

[`getch_data`][pokelance.client.async_client.PokeLanceAsyncClient.getch_data] dynamically dispatches cache-then-fetch operations by extension and category name:

=== "Async"

    ```python exec="true" source="above" result="text" session="getch_async"
    import asyncio
    from pokelance import PokeLanceAsyncClient
    from pokelance.constants import ExtensionEnum


    async def main() -> None:
        async with PokeLanceAsyncClient() as client:
            pokemon = await client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
            print(f"{pokemon.name} (#{pokemon.id})")


    asyncio.run(main())
    ```

=== "Sync"

    ```python exec="true" source="above" result="text" session="getch_sync"
    from pokelance import PokeLanceSyncClient
    from pokelance.constants import ExtensionEnum

    with PokeLanceSyncClient() as client:
        pokemon = client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
        print(f"{pokemon.name} (#{pokemon.id})")
    ```

`ext` accepts an [`ExtensionEnum`][pokelance.constants.ExtensionEnum] member or a string (e.g. `"pokemon"`, `"berry"`).

!!! tip "Bidirectional Type Inference"
    In PokeLance, `getch_data` and `from_url` are generic over `BaseModelT`. If you annotate your target variable, type checkers (Ty, Pyright, Mypy) will automatically contextualize the return type:

    ```python
    from pokelance.models import Pokemon

    pokemon: Pokemon = await client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    ```

## Constructing requests from a URL: `from_url`

PokéAPI payloads frequently include resource URLs (e.g. `"url": "https://pokeapi.co/api/v2/pokemon/1/"`). [`from_url`][pokelance.client.async_client.PokeLanceAsyncClient.from_url] resolves them straight into model instances:

```python exec="true" source="above" result="text" session="fromurl"
import asyncio
from pokelance import PokeLanceAsyncClient
from pokelance.models import Pokemon


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        pokemon: Pokemon = await client.from_url("https://pokeapi.co/api/v2/pokemon/25/")
        print(f"{pokemon.name} (#{pokemon.id})")


asyncio.run(main())
```

Internally, this is powered by [`ExtensionEnum.validate_url`][pokelance.constants.ExtensionEnum.validate_url].

## Summary

| Need                                             | Async Method                                  | Sync Method                                 |
| ------------------------------------------------ | --------------------------------------------- | ------------------------------------------- |
| Cache-only lookup, no network                    | `client.<ext>.get_<category>(...)`            | `client.<ext>.get_<category>(...)`          |
| Network fallback, single known extension         | `await client.<ext>.fetch_<category>(...)`    | `client.<ext>.fetch_<category>(...)`        |
| Extension/category chosen dynamically at runtime | `await client.getch_data(ext, category, id_)` | `client.getch_data(ext, category, id_)`     |
| Fetch model directly from PokéAPI resource URL   | `await client.from_url(url)`                  | `client.from_url(url)`                      |
