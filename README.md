<h1 align="center"><b>PokeLance</b></h1>
<p align="center">
<img src="https://raw.githubusercontent.com/FallenDeity/PokeLance/master/docs/assets/pokelance.png" width=450 alt="logo"><br><br>
<img src="https://img.shields.io/github/license/FallenDeity/PokeLance?style=flat-square" alt="license">
<img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
<img src="https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat-square" alt="mypy">
<img src="https://img.shields.io/badge/%20linter-ruff-%231674b1?style=flat-square" alt="ruff">
<img src="https://img.shields.io/github/stars/FallenDeity/PokeLance?style=flat-square" alt="stars">
<img src="https://img.shields.io/github/last-commit/FallenDeity/PokeLance?style=flat-square" alt="commits">
<img src="https://img.shields.io/pypi/pyversions/PokeLance?style=flat-square" alt="py">
<img src="https://img.shields.io/pypi/v/PokeLance?style=flat-square" alt="versions">
<br><br>
A flexible, statically typed and easy to use pokeapi wrapper for python 🚀
</p>

---


Features:
- Modern and pythonic API asynchronously built on top of aiohttp
- Flexible and easy to use
- Statically typed with mypy
- Linted with ruff
- Well documented
- Optimized for speed and performance
- Automatically caches data for faster access
- Caches endpoints for user convenience

---

## Installation

```bash
$ python -m pip install PokeLance
```

---

## Usage

```python
import asyncio

from pokelance import PokeLance

client = PokeLance()  # Create a client instance


async def main() -> None:
    print(await client.ping())  # Ping the pokeapi
    print(await client.berry.fetch_berry("cheri"))  # Fetch a berry from the pokeapi
    print(await client.berry.fetch_berry_flavor("spicy"))
    print(await client.berry.fetch_berry_firmness("very-soft"))
    print(client.berry.get_berry("cheri"))  # Get a cached berry it will return None if it doesn't exist
    print(client.berry.get_berry_flavor("spicy"))
    print(client.berry.get_berry_firmness("very-soft"))
    await client.close()  # Close the client
    return None


asyncio.run(main())
```

## With Async Context Manager

```python
import asyncio

import aiohttp
from pokelance import PokeLance


async def main() -> None:
    # Use an async context manager to create a client instance
    async with aiohttp.ClientSession() as session, PokeLance(session=session) as client:
        print(await client.ping())  # Ping the pokeapi
        print(await client.berry.fetch_berry("cheri"))  # Fetch a berry from the pokeapi
        print(await client.berry.fetch_berry_flavor("spicy"))
        print(await client.berry.fetch_berry_firmness("very-soft"))
        print(client.berry.get_berry("cheri"))  # Get a cached berry it will return None if it doesn't exist
        print(client.berry.get_berry_flavor("spicy"))
        print(client.berry.get_berry_firmness("very-soft"))
        # The client will be closed automatically when the async context manager exits
    return None

asyncio.run(main())
```

## Important Links


- [PokeAPI](https://pokeapi.co/)
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)
- [PokeLance Documentation](https://FallenDeity.github.io/PokeLance/)
- [PokeLance ReadTheDocs](https://pokelance.readthedocs.io/en/latest/)
- [PokeLance GitHub](https://github.com/FallenDeity/PokeLance)
- [PokeLance PyPI](https://pypi.org/project/PokeLance/)
- [PokeLance Discord](https://discord.gg/yeyEvT5V2J)

---

!!! note "Note"
    This is a work in progress. If you find any bugs or have any suggestions, please open an issue [here](https://github.com/FallenDeity/PokeLance/issues/new).

---
