import asyncio

from pokelance import PokeLance

client = PokeLance()


async def main() -> None:
    print(await client.ping())
    print(await client.berry.fetch_berry("cheri"))
    print(await client.berry.fetch_berry_flavor("spicy"))
    print(await client.berry.fetch_berry_firmness("very-soft"))
    print(client.berry.get_berry("cheri"))
    print(client.berry.get_berry_flavor("spicy"))
    print(client.berry.get_berry_firmness("very-soft"))
    await client.close()
    return None


asyncio.run(main())
