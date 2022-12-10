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


# case 1
async def main() -> None:
    client = pokelance.PokeLance()
    print(await client._client.ping())
    return None


asyncio.run(main())
