import asyncio

from pokelance import PokeLance


async def main() -> None:
    client = PokeLance()
    # mon = await client.pokemon.fetch_pokemon("pichu")
    # print(mon.forms)
    print(await client.ping())
    # ab = (await client.pokemon.fetch_ability("static"))
    # print(ab.name)
    await asyncio.sleep(10)
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
