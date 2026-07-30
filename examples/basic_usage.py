import asyncio

from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    print(await client.ping())
    pokemon = await client.pokemon.fetch_pokemon("pikachu")
    print(pokemon.sprites.other.showdown)
    await client.close()
    return None


asyncio.run(main())
