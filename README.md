<h1 align="center"><b>PokeLance</b></h1>
<p align="center">
<img src="https://raw.githubusercontent.com/FallenDeity/PokeLance/master/docs/assets/pokelance.png" width=450 alt="logo"><br><br>
<img src="https://img.shields.io/github/license/FallenDeity/PokeLance?style=flat-square" alt="license">
<img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
<img src="https://img.shields.io/badge/type_checker-ty-%231674b1?style=flat-square" alt="ty">
<img src="https://img.shields.io/badge/linter-ruff-%231674b1?style=flat-square" alt="ruff">
<img src="https://img.shields.io/github/stars/FallenDeity/PokeLance?style=flat-square" alt="stars">
<img src="https://img.shields.io/pypi/dm/pokelance.svg" alt="downloads">
<img src="https://img.shields.io/github/last-commit/FallenDeity/PokeLance?style=flat-square" alt="commits">
<img src="https://img.shields.io/pypi/pyversions/PokeLance?style=flat-square" alt="py">
<img src="https://img.shields.io/pypi/v/PokeLance?style=flat-square" alt="versions">
<br><br>
A flexible, statically typed and easy to use PokéAPI wrapper for Python 🚀
</p>

---

### Features:

- **Dual Client Architecture**: Full support for both Asynchronous (`PokeLanceAsyncClient`) and Synchronous (`PokeLanceSyncClient`) paradigms.
- **Modern HTTP Engine**: Built on top of [`niquests`](https://github.com/jawah/niquests) with HTTP/2 and HTTP/3 support.
- **Statically Typed**: Fully typed with strict typing support using [`ty`](https://github.com/astral-sh/ty).
- **Automatic Caching**: Dual-level caching with in-memory LRU model caches, endpoint pre-warming, and disk serialization.
- **Media Helpers**: Built-in async and sync media loaders (`get_image`, `get_audio`) with dedicated caching.
- **Developer Experience**: Fuzzy "did you mean...?" suggestions on invalid lookups and structured logging.

---

## Installation

```bash
# Using uv (recommended)
$ uv add git+https://github.com/FallenDeity/PokeLance.git@beta-v1

# Using pip
$ python -m pip install -U git+https://github.com/FallenDeity/PokeLance.git@beta-v1
```

---

## Quickstart

### Asynchronous Client

```python
import asyncio
from pokelance import PokeLanceAsyncClient


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        print(await client.ping())

        # Fetch from network (and populate LRU cache)
        berry = await client.berry.fetch_berry("cheri")
        print(f"Fetched: {berry.name} (id={berry.id})")

        # Instant synchronous cache lookup
        cached_berry = client.berry.get_berry("cheri")
        print(f"Cached: {cached_berry}")


asyncio.run(main())
```

### Synchronous Client

```python
from pokelance import PokeLanceSyncClient

with PokeLanceSyncClient() as client:
    print(client.ping())

    berry = client.berry.fetch_berry("cheri")
    print(f"Fetched: {berry.name} (id={berry.id})")

    cached_berry = client.berry.get_berry("cheri")
    print(f"Cached: {cached_berry}")
```

---

## Documentation

- [Getting Started](https://fallendeity.github.io/PokeLance/)
- [Quickstart](https://fallendeity.github.io/PokeLance/guide/quickstart/)
- [Fetching Data](https://fallendeity.github.io/PokeLance/guide/fetching_data/)
- [Caching In Depth](https://fallendeity.github.io/PokeLance/guide/caching/)
- [Error Handling](https://fallendeity.github.io/PokeLance/guide/error_handling/)
- [Media - Sprites & Cries](https://fallendeity.github.io/PokeLance/guide/media/)
- [API Reference](https://fallendeity.github.io/PokeLance/api_reference/pokelance/)

---

## Important Links

- [PokeAPI](https://pokeapi.co/)
- [PokeLance Documentation](https://fallendeity.github.io/PokeLance/)
- [PokeLance GitHub](https://github.com/FallenDeity/PokeLance)
- [PokeLance PyPI](https://pypi.org/project/PokeLance/)
