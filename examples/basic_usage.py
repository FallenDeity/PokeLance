import asyncio

from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    print(await client.ping())
    x = await client.pokemon.fetch_pokemon_form("charmander")
    print(x.to_dict())
    return None


asyncio.run(main())
