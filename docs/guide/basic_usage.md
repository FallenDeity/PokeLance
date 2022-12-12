# Basic Use and taking advantage of cache

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
