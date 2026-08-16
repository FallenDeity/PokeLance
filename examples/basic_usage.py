from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import pokelance
from pokelance.constants import ExtensionEnum

if TYPE_CHECKING:
    from pokelance.models import Pokemon

client = pokelance.PokeLanceAsyncClient(log_level=logging.DEBUG)


async def main() -> None:
    await client.wait_until_ready()
    client.berry.cache_group.reset()
    await client.berry.setup()
    print(f"Latency: {await client.ping()}")
    await client.berry.cache_group.wait_until_ready()
    print(await client.berry.fetch_berry("cheri"))

    pokemon: Pokemon = await client.getch_data(ExtensionEnum.Pokemon, "pokemon", 1)
    print(f"Fetched Pokemon: {pokemon.name} (ID: {pokemon.id})")

    await client.close()


asyncio.run(main())
