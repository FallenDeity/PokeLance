![](./assets/pokelance.png){align=left style="width: 300px;"}

# Welcome to PokeLance's documentation.

![](https://img.shields.io/github/license/FallenDeity/PokeLance?style=flat-square)
![](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)
![](https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat-square)
![](https://img.shields.io/badge/%20linter-ruff-%231674b1?style=flat-square)
![](https://img.shields.io/github/stars/FallenDeity/PokeLance?style=flat-square)
![](https://img.shields.io/github/last-commit/FallenDeity/PokeLance?style=flat-square)
![](https://img.shields.io/pypi/pyversions/PokeLance?style=flat-square)
![](https://img.shields.io/pypi/v/PokeLance?style=flat-square)

A [WIP] flexible and easy to use pokeapi wrapper for python 🚀

---

## Installation

```bash
python -m pip install pokelance
```

---

## Important Links

- [PokeAPI](https://pokeapi.co/)
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)
- [PokeLance Documentation](https://FallenDeity.github.io/PokeLance/)
- [PokeLance GitHub](https://github.com/FallenDeity/PokeLance)
- [PokeLance PyPI](https://pypi.org/project/PokeLance/)
- [PokeLance Discord](https://discord.gg/FyEE54u9GF)

---

## Basic Usage

```python
import asyncio

from pokelance import PokeLance

client = PokeLance()


async def main():
    print(await client.ping())
    print(await client.berry.fetch_berry("cheri"))
    print(await client.berry.fetch_berry_flavor("spicy"))
    print(await client.berry.fetch_berry_firmness("very-soft"))
    print(client.berry.get_berry("cheri"))
    print(client.berry.get_berry_flavor("spicy"))
    print(client.berry.get_berry_firmness("very-soft"))
    return None


asyncio.run(main())
```

---

!!! note "Note"
    This is a work in progress. If you find any bugs or have any suggestions, please open an issue [here](https://github.com/FallenDeity/PokeLance/issues/new).

---
