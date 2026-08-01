import asyncio

from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    await client.wait_until_ready()
    client.berry.cache.reset()
    await client.berry.setup()
    await client.berry.cache.wait_until_ready()
    print(await client.berry.fetch_berry("chery"))
    return None


asyncio.run(main())
