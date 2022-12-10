import asyncio

import pokelance

"""
# case 2
client = pokelance.PokeLance()
async def main():
    print(await client._client.ping())
    return None
asyncio.run(main())

# case 3
async def main():
    async with pokelance.PokeLance() as client:
        print(await client._client.ping())
        return None
asyncio.run(main())
"""

client = pokelance.PokeLance()


# case 1
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
