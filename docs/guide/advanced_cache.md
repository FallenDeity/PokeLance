# Advanced usage of cache

```python
import asyncio

import pokelance


async def main():
    client = pokelance.PokeLance()
    client.logger.info(await client.ping())
    client.logger.info(f"Size: {len(client.berry.cache.berry_flavor)}")
    try:
        client.logger.info("Loading berry flavors from cache...")
        await client.berry.cache.berry_flavor.load()
    except FileNotFoundError:
        client.logger.info("Loading berry flavors from API...")
        await client.berry.cache.berry_flavor.wait_until_ready()
        await client.berry.cache.berry_flavor.load_all()
        await client.berry.cache.berry_flavor.save()
    client.logger.info(f"Loaded {len(client.berry.cache.berry_flavor)} berry flavors.")
    await client.close()


asyncio.run(main())
```

## Explanation

Code first looks up the main project directory if the results are already stored if not it tries to load from the api.
The `wait_until_ready()` method checks if the endpoints are cached to load all the data. Another feature of the endpoint cache is input validation in run time and auto completes.

!!! Note
    The data is stored in a `json` file and you can provide path where its to be stored and loaded from.
