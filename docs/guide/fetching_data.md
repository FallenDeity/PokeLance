# Fetching Data

PokeLance exposes every PokéAPI resource through a consistent, predictable pattern repeated
across all 11 extensions and ~60 categories. Learn it once here and you already know how to
use the entire library.

## The `get_*` / `fetch_*` pair

Every category (`berry`, `pokemon`, `move-target`, ...) gets exactly two methods:

``` mermaid
flowchart LR
    A["client.berry.get_berry('cheri')"] -->|cache hit| B(Berry instance)
    A -->|cache miss| C[None]
    D["await client.berry.fetch_berry('cheri')"] -->|cache hit| B
    D -->|cache miss| E[GET pokeapi.co/api/v2/berry/cheri] --> F[cache the result] --> B
```

- **`get_<category>(name_or_id)`**: synchronous, cache-only. Returns the cached model, or
  `None` if it hasn't been fetched yet. Never touches the network.
- **`fetch_<category>(name_or_id)`**: asynchronous. Returns the cached model if present,
  otherwise makes a request, caches the parsed model, and returns it.

```python
berry = client.berry.get_berry("cheri")          # None the first time
berry = await client.berry.fetch_berry("cheri")  # network + cache
berry = client.berry.get_berry("cheri")          # now cached, instant
```

Both accept either the resource's **name** (`str`) or **id** (`int`) interchangeably:

```python
await client.pokemon.fetch_pokemon("bulbasaur")
await client.pokemon.fetch_pokemon(1)  # same resource
```

## Validation and "did you mean...?"

Before either method touches the cache, an internal validation step on
[`BaseExtension`][pokelance.ext._base.BaseExtension] checks the requested name/id against
the extension's pre-loaded endpoint registry (see
[Configuration](configuration.md#disabling-endpoint-pre-loading)). If it isn't a known
resource, a [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] is raised
immediately, with close-match suggestions attached, powered by `difflib`:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLance
from pokelance.exceptions import ResourceNotFound

client = PokeLance()


async def main() -> str:
    await client.wait_until_ready()
    try:
        await client.berry.fetch_berry("chery")  # typo for "cheri"
    except ResourceNotFound as exc:
        return str(exc)
    finally:
        await client.close()
    return "no error raised"


print(asyncio.run(main()))
```

The suggestions are also available as an attribute on the exception itself, as `exc.suggestions` (a plain `List[str]` or `None`):

```python
try:
    await client.berry.fetch_berry("chery")
except ResourceNotFound as exc:
    print(exc.suggestions)  # ['cheri']
```

See [Error Handling](error_handling.md) for the full exception hierarchy.

## One call for any extension: `getch_data`

Writing `client.<extension>.get_x(...)  or  await client.<extension>.fetch_x(...)`
everywhere gets repetitive once you're working across many extensions dynamically (for
example, building a generic lookup utility). [`getch_data`][pokelance.client.PokeLance.getch_data]
does both steps for you, dispatching by extension and category name:

```python exec="true" source="above" result="text" session="getch"
import asyncio
from pokelance import PokeLance
from pokelance.constants import ExtensionEnum

client = PokeLance()


async def main() -> str:
    pokemon = await client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    await client.close()
    return f"{pokemon.name} (#{pokemon.id})"


print(asyncio.run(main()))
```

`ext` accepts an [`ExtensionEnum`][pokelance.constants.ExtensionEnum] member, or just a
plain string (case-insensitively titled internally):

```python
await client.getch_data("pokemon", "pokemon", "pikachu")
await client.getch_data("berry", "berry_flavor", "spicy")  # underscores or hyphens both work
```

Invalid extensions or categories raise a plain `ValueError` (not `ResourceNotFound`, that's
reserved for invalid resource names within a valid category):

```python exec="true" source="above" result="text" session="getch"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    try:
        await client.getch_data("berry", "not-a-real-category", "cheri")
    except ValueError as exc:
        return str(exc)
    finally:
        await client.close()
    return "no error"


print(asyncio.run(main()))
```

!!! warning "You lose static type information"
    `getch_data` (and `from_url` below) are typed to return a generic `BaseType` bound to
    `BaseModel`, since the extension/category is only known at runtime, not at type-check
    time. Your type checker will see `BaseModel`, not `Pokemon` or `Berry`. If you need
    precise typing at the call site, annotate it yourself:

    ```python
    from pokelance.models import Pokemon

    pokemon: Pokemon = await client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    ```

    This is purely a static-analysis concern, the object returned at runtime is still the
    correct concrete model; only your type checker's view of it is widened.

## Constructing requests from a URL: `from_url`

PokéAPI responses are full of cross-references as URLs
(`"url": "https://pokeapi.co/api/v2/pokemon/1/"`). Rather than manually parsing those,
[`from_url`][pokelance.client.PokeLance.from_url] resolves them straight into the right
model via the same cache-then-fetch path as `getch_data`:

```python exec="true" source="above" result="text" session="fromurl"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    pokemon = await client.from_url("https://pokeapi.co/api/v2/pokemon/25/")
    await client.close()
    return f"{pokemon.name} (#{pokemon.id})"


print(asyncio.run(main()))
```

Internally this is powered by
[`ExtensionEnum.validate_url`][pokelance.constants.ExtensionEnum.validate_url], which
pattern matches the URL's category segment (`EXTENSION_PATTERN` in `pokelance.constants`)
against every registered extension's categories, then delegates to `getch_data`, so the same
type-erasure caveat above applies here too. An unrecognized host or category raises
`ValueError`.

## Summary

| Need                                             | Use                                           |
| ------------------------------------------------ | --------------------------------------------- |
| Cache-only lookup, no network                    | `client.<ext>.get_<category>(...)`            |
| Network fallback, single known extension         | `await client.<ext>.fetch_<category>(...)`    |
| Extension/category chosen dynamically at runtime | `await client.getch_data(ext, category, id_)` |
| You already have a PokéAPI resource URL          | `await client.from_url(url)`                  |
